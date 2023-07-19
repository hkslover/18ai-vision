
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <windows.h>
#define MAX_GENTIMES 50
#define MAX_POINT_COUNTS 50
#define INDIVIDUAL_COUNTS 100
#define CROSS_P 0.5
#define MUTATION_P 0.03
int point_counts = 13;
int individual[INDIVIDUAL_COUNTS][MAX_POINT_COUNTS];
int selected_individual[INDIVIDUAL_COUNTS][MAX_POINT_COUNTS];
double fitness[INDIVIDUAL_COUNTS];
double min_distance = 99999.;
int best_individual[MAX_POINT_COUNTS];
double total_fitness = 0.;
int _x[13] = { 4, 8, 14, 28, 13, 19, 25, 3, 7, 25, 28, 33};
int _y[13] = { 5, 7, 5, 7, 9, 13, 14, 18, 21, 22, 20, 23};
//int visited_hash[13];
//int point_counts = 13;
int out_tsp[13][2];

// #define MAX_GENTIMES 350
// #define MAX_POINT_COUNTS 20
// #define INDIVIDUAL_COUNTS 750
// int individual[INDIVIDUAL_COUNTS][MAX_POINT_COUNTS];
// double fitness[INDIVIDUAL_COUNTS];
// double min_distance = 99999;
// int best_individual[MAX_POINT_COUNTS];
// int out_tsp[60][2];   
inline void copy1(int* src, int* dst) {
	for (int i = 0; i < point_counts; i++)
		dst[i] = src[i];
}
double get_distance(int x1, int y1, int x2, int y2) {
	return sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2));
}
double get_individual_distance(int* a) {
	double sum = 0;
	int j = 0;
	for (j = 0; j < point_counts - 1; j++) {
		int first_point_index = a[j];
		int second_point_index = a[j + 1];
		sum += get_distance(_x[first_point_index], _y[first_point_index], _x[second_point_index], _y[second_point_index]);
	}
	/*计算第一个点和最后一个点的距离*/
	sum += get_distance(_x[a[0]], _y[a[0]], _x[a[point_counts-1]], _y[a[point_counts - 1]]);
	return sum;
}
/*获取当前个体中路径最优的并放到best中，同时计算每个个体的fitness*/
void get_distance_fitness(void) {
	double dis = 0.;
	int min_distance_individual_index = 0;
	total_fitness = 0.;
	for (int j = 0; j < INDIVIDUAL_COUNTS; j++)
	{
		dis = get_individual_distance(individual[j]);
		fitness[j] = 1. / dis; 
		total_fitness += fitness[j];
		if (dis < min_distance) {
			min_distance = dis;
			copy1(individual[j], best_individual);
		}
	}
	
}
void init(void) {
	int num = 0;
	while (num < INDIVIDUAL_COUNTS)
	{
		for (int i = 0; i < INDIVIDUAL_COUNTS; i++)
			for (int j = 0; j < point_counts; j++)
				individual[i][j] = j;
		num++;
		for (int i = 0; i < point_counts - 1; i++)
		{
			for (int j = i + 1; j < point_counts; j++)
			{
				int temp = individual[num][i];
				individual[num][i] = individual[num][j];
				individual[num][j] = temp;
				num++;
				if (num >= INDIVIDUAL_COUNTS)
					break;
			}
			if (num >= INDIVIDUAL_COUNTS)
				break;
		}
		while (num < INDIVIDUAL_COUNTS)
		{
			double r1 = ((double)rand()) / (RAND_MAX);
			double r2 = ((double)rand()) / (RAND_MAX);
			int p1 = (int)(point_counts * r1);
			int p2 = (int)(point_counts * r2);
			int temp = individual[num][p1];
			individual[num][p1] = individual[num][p2];
			individual[num][p2] = temp;
			num++;
		}
	}
	//	int i,j,k,n = 0;
	//	for (i = 0; i < INDIVIDUAL_COUNTS; i++) {
	//		for (j = 0; j < point_counts; j++) {
	//			individual[i][j] = j;
	//		}
	//		/*随机打乱每个个体中的点坐标索引*/
	//		for (k = point_counts - 1; k > 0; k--) {
	//			n = rand() % (k + 1);
	//			int temp = individual[i][k];
	//			individual[i][k] = individual[i][n];
	//			individual[i][n] = temp;
	//		}
	//	}
}

void roulette_wheel_selection(void) {
	
	double probability[INDIVIDUAL_COUNTS];
	for (int j = 0; j < INDIVIDUAL_COUNTS; j++)
	{
		probability[j] = fitness[j] / total_fitness; // 概率数组
	}
	for (int i = 0; i < INDIVIDUAL_COUNTS; i++) {
		double r = (double)rand() / RAND_MAX;
		double sum = 0.0;
		for (int j = 0; j < INDIVIDUAL_COUNTS; j++) {
			sum += probability[j];
			if (r <= sum) { // 找到第一个满足条件的个体
				copy1(individual[j], selected_individual[i]);
				break;
			}
		}
	}
	memcpy(individual, selected_individual, INDIVIDUAL_COUNTS * MAX_POINT_COUNTS * sizeof(int));
}

int check(int gens[], int r1, int r2, int* index) {
	int hash_table[MAX_POINT_COUNTS] = { 0 };
	for (int i = r1; i <= r2; i++)
	{
		hash_table[gens[i]] = 1;
	}
	for (int i = 0; i < point_counts; i++)
	{
		if (i >= r1 && i <= r2) continue;
		if (hash_table[gens[i]]) {
			*index = i;
			return 1;
		}
	}
	return 0;
}
inline int get_gens_index(int exchange[], int exchange_counts, int gens) {
	for (int i = 0; i < exchange_counts; i++)
	{
		if (exchange[i] == gens) {
			return i;
		}
	}
}
void intercross(int* individual_a, int* individual_b) {
	int r1 = rand() % point_counts;
	int r2 = rand() % point_counts;
	// 保证 r1 != r2
	while (r1 == r2) {
		r2 = rand() % point_counts;
	}
	// 保证r1 < r2 
	if (r1 > r2) {
		int temp = r1;
		r1 = r2;
		r2 = temp;
	}
	/*printf("r1=%d r2=%d", r1, r2);*/
	/*保存重组段*/
	int exchange_counts = r2 - r1 + 1;
	int exchange_a[MAX_POINT_COUNTS] = { 0 };
	int exchange_b[MAX_POINT_COUNTS] = { 0 };
	int _r1 = r1;
	for (int i = 0; i < exchange_counts; i++) {
		exchange_a[i] = individual_a[_r1];
		exchange_b[i] = individual_b[_r1];
		_r1++;
	}
	_r1 = r1;
	/*交换重组段*/
	for (int i = 0; i < exchange_counts; i++) {
		individual_a[_r1] = exchange_b[i];
		individual_b[_r1] = exchange_a[i];
		_r1++;
	}
	int conflict_index = 0;
	while (check(individual_a, r1, r2, &conflict_index)) {
		int conflict_index_in_b = get_gens_index(exchange_b, exchange_counts, individual_a[conflict_index]);
		individual_a[conflict_index] = exchange_a[conflict_index_in_b];
	}
	while (check(individual_b, r1, r2, &conflict_index)) {
		int conflict_index_in_a = get_gens_index(exchange_a, exchange_counts, individual_b[conflict_index]);
		individual_b[conflict_index] = exchange_b[conflict_index_in_a];
	}
}

void cross(void) {
	int index = 0;
	while (index < point_counts - 1) {
		
		if ((double)rand() / RAND_MAX > CROSS_P) {
			index += 2;
			continue;
		}
		intercross(individual[index], individual[index+1]);
		index += 2;
	}
	
}
void mutate(void) {
	for (int i = 0; i < INDIVIDUAL_COUNTS; i++) {
		if ((double)rand() / RAND_MAX < MUTATION_P) {
			
			int r1 = rand() % point_counts;
			int r2 = rand() % point_counts;
			
			//保证 r1 != r2
			while (r1 == r2) {
				r2 = rand() % point_counts;
			}
			int temp = individual[i][r1];
			individual[i][r1] = individual[i][r2];
			individual[i][r2] = temp;
		}
	}
}
void reverse(void)
{
	double pick1, pick2;
	double dis, reverse_dis;
	int n;
	int flag, pos1, pos2, temp;
	int reverse_arr[MAX_POINT_COUNTS];
	
	for (int i = 0; i < INDIVIDUAL_COUNTS; i++)
	{
		flag = 0; // 用于控制本次逆转是否有效
		while (flag == 0)
		{
			pick1 = ((double)rand()) / (RAND_MAX);
			pick2 = ((double)rand()) / (RAND_MAX);
			pos1 = (int)(pick1 * point_counts); // 选取进行逆转操作的位置
			pos2 = (int)(pick2 * point_counts);
			while (pos1 > point_counts - 1)
			{
				pick1 = ((double)rand()) / (RAND_MAX);
				pos1 = (int)(pick1 * point_counts);
			}
			while (pos2 > point_counts - 1)
			{
				pick2 = ((double)rand()) / (RAND_MAX);
				pos2 = (int)(pick2 * point_counts);
			}
			if (pos1 > pos2)
			{
				temp = pos1;
				pos1 = pos2;
				pos2 = temp; // 交换使得pos1 <= pos2
			}
			if (pos1 < pos2)
			{
				for (int j = 0; j < point_counts; j++)
					reverse_arr[j] = individual[i][j]; // 复制数组
				n = 0; // 逆转数目
				for (int j = pos1; j <= pos2; j++)
				{
					reverse_arr[j] = individual[i][pos2 - n]; // 逆转数组
					n++;
				}
				reverse_dis = get_individual_distance(reverse_arr); // 逆转之后的距离
				dis = get_individual_distance(individual[i]); // 原始距离
				if (reverse_dis < dis)
				{
					for (int j = 0; j < point_counts; j++)
						individual[i][j] = reverse_arr[j]; // 更新个体
				}
			}
			flag = 1;
		}
		
	}
}
void tsp(void)
{

	//srand(time(NULL));
	_x[12] = 2;
	_y[12] = 2;
	init();
	get_distance_fitness();
	out_tsp[0][0] = 2;
	out_tsp[0][1] = 2;

	for (int i = 0; i < MAX_GENTIMES; i++)
	{
		roulette_wheel_selection();
		cross();
		mutate();
		reverse();
		get_distance_fitness();

	}
	int init_points_index = 0;
	for (int i = 0; i < point_counts; i++)
	{
		if(_x[best_individual[i]] == 2 && _y[best_individual[i]] == 2)
		{
			init_points_index = i;
			break;
		}

	}

	for (int i = init_points_index; i < point_counts+init_points_index; i++)
	{	
		out_tsp[i-init_points_index][0]=_x[best_individual[i%point_counts]];
		out_tsp[i-init_points_index][1]=_y[best_individual[i%point_counts]];

	}

}
//void greedy(void)
//{
//	_x[12] = 2;
//	_y[12] = 2;
//	out_tsp[0][0] = 2;
//	out_tsp[0][1] = 2;
//	visited_hash[12] = 1;
//	int index = 12;
//	int out_index = 1;
//	for (int i = 0; i < point_counts-1; ++i)
//	{
//		int next_index = -1;
//		double min_distance = 9999.;
//		for (int j = 0; j < point_counts; ++j)
//		{
//			if(visited_hash[j] == 1)
//				continue;
//			double distance = get_distance(_x[index],_y[index],_x[j],_y[j]);
//			if(distance < min_distance)
//			{
//				min_distance = distance;
//				next_index = j;
//			}
//			
//		}
////		printf("(%d,%d) \n",_x[next_index],_y[next_index]);
//		out_tsp[out_index][0] = _x[next_index];
//		out_tsp[out_index][1] = _y[next_index];
//		out_index++;
//		visited_hash[next_index] = 1;
//		index = next_index;
//	}
////	for(int i=0;i<point_counts;i++){
////		printf("(%d,%d) \n",out_tsp[i][0],out_tsp[i][1]);
////	}
//}	

int main()
{
	tsp();
	for(int i=0;i<point_counts;i++){
		printf("(%d,%d) \n",out_tsp[i][0],out_tsp[i][1]);
	}
	return 0;
}
