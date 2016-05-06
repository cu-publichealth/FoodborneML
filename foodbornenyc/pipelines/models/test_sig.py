from scipy.special import comb
import math

def exp_auc(m, n, k):
    exp = 1 - (k / (m + n))
    snd = ( (n - m)**2 * (m + n + 1))/(4 * m * n)
    sum_1 = 0.0
    for x in range(int(k)):
        sum_1 += comb(m+n, x)
    sum_2 = 0.0
    for x in range(int(k)+1):
        sum_2 += comb(m+n+1, x)
    snd = snd * ( k / (m + n) - (sum_1 / sum_2))
    return exp - snd

def cal_x_sub_q(q, m, n, k, N):
    sum = 0.0
    for x in range(0, k + 1):
        first_term = x**q
        M = m - (k - x) + x
        M_prime = n + (k - x) - x
        x_prime = k - x
        second_term = comb(M, x)
        third_term = comb(M_prime, x_prime)

def get_t(m, n):
    return (3 * (( (m - n) ** 2) + m + n) + 2)

def z_sub_i(m, n, k, i):
    numerator = 0
    for x in range(int(k) - i + 1):
        numerator += comb(m + n + 1 - i, x)

    denominator = 0
    for x in range(int(k) + 1):
        denominator += comb(m + n + 1, x)

    return (1.0 * numerator) / denominator

def q_sub_0(m, n, t, k):
    first_term = (m + n + 1) * t * (k ** 2)
    second_term =  (( (-3 * (n**2)) + (3 * m * n) + (3 * m) + 1) * t -
                      12 * ( (3* m * n) + m + n) - 8) * k
    third_term = ( (-3 * (m ** 2)) + (7 * m) + (10 * n) + (3 * m * n) + 10) * t
    fourth_term = 4 * ( (3 * m * n) + m + n + 1)
    return first_term + second_term + third_term - fourth_term

def q_sub_1(m, n, t, k):
    first_term = t * (k ** 3)
    second_term = 3 * (m - 1) * t * (k ** 2)
    third_term = (( (-3 * (n ** 2)) + (3 * m * n) - (3 * m) + 8) * t - 6 *
                  ( (6 * m * n) + m + n)) * k
    fifth_term = ( (-3 * (m ** 2)) + (7 * (m + n)) + (3 * m * n)) * t
    sixth_term = 2 * ( (6 * m * n) + m + n)
    return (first_term + second_term + third_term + fifth_term - sixth_term)


def variance(m, n, k): 
    t = get_t(m, n)
    z_4 = z_sub_i(m, n, k, 4)
    z_3 = z_sub_i(m, n, k, 3)
    z_2 = z_sub_i(m, n, k, 2)
    z_1 = z_sub_i(m, n, k, 1)
    q_1 = q_sub_1(m, n, t, k)
    q_0 = q_sub_0(m, n, t, k)
    '''print "t: " + str(t)
    print "z4: " + str(z_4)
    print "z3: " + str(z_3)
    print "z2: " + str(z_2)
    print "z1: " + str(z_1)
    print "q0: " + str(q_0)
    print "q1: " + str(q_1)'''
    first_term_numerator = ((m + n + 1) * (m + n) * (m + n - 1) * t *
                             ((m + n - 2) * z_4 - ( (2 * m) - n + (3 * k) - 10)*
                                  z_3))

    first_term_denominator = 72 * (m ** 2) * (n ** 2)
    first_term = first_term_numerator * 1.0 / first_term_denominator
    second_term_numerator = ((m + n + 1) * (m + n) * t *
                             ((m ** 2) - (n * m) + (3 * k * m) - (5 * m) +
                               (2 * (k ** 2)) - (n * k) + 12 - (9 * k))
                             * z_2 )

    second_term_denominator = 48 * (m ** 2) * (n ** 2)
    third_term_numerator = (((m + n + 1) ** 2) * ((m - n) ** 4) * (z_1 ** 2))
    third_term_denominator = 16 * (m**2) * (n**2)
    fourth_term_numerator = (m + n + 1) * q_1 * z_1
    fourth_term_denominator = 72 * (m ** 2) * (n ** 2)
    fifth_term_numerator = k * q_0
    fifth_term_denominator = 144 * (m ** 2) * (n ** 2)

    '''print first_term_numerator / first_term_denominator
    print second_term_numerator / second_term_denominator
    print third_term_numerator / third_term_denominator
    print fourth_term_numerator / fourth_term_denominator
    print fifth_term_numerator / fifth_term_denominator'''

    return ( (first_term_numerator / first_term_denominator) +
             (second_term_numerator / second_term_denominator) -
             (third_term_numerator / third_term_denominator) -
             (fourth_term_numerator / fourth_term_denominator) +
             (fifth_term_numerator / fifth_term_denominator) )


def print_results(auc, stdev, alpha_level):
    print "auc was: " + str(auc)
    print "st dev: " + str(stdev)
    max_auc = auc + (stdev / math.sqrt(alpha_level))
    min_auc = auc - (stdev / math.sqrt(alpha_level))
    print "confidence interval: [" + str(min_auc) + ", " + str(max_auc) + "]"

    
def main():
    m = 23 + 126.0 # number of positive examples (TP + FN)
    n = 98 + 32.0  # number of negative examples (FP + TN)
    k = 23 + 32.0  # incorrectly classified reviews (FP + FN)
    N = m + n #total number of reviews

    print "Logistic Regression Classifier"
    print variance(m, n, k)
    print_results(0.8878, math.sqrt(variance(m, n, k)), 0.05)
    print exp_auc(m, n, k)
    print "~~~~~~~~~~~~~~~~~~~~~~~~"
    print "SVM Regression Classifier"
    k = 41
    print_results(0.8872, math.sqrt(variance(m, n, k)), 0.05)
    print "~~~~~~~~~~~~~~~~~~~~~~~~"
    print "RF"
    k = 44
    print_results(0.868, math.sqrt(variance(m, n, k)), 0.05)
    print "~~~~~~~~~~~~~~~~~~~~~~~~"
    print "Old Classifier"
    k = 144.0
    print "old var: " + str(variance(m, n, k))
    print_results(0.65, math.sqrt(variance(m, n, k)), 0.05)

    
main()    
