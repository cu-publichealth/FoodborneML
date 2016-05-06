from scipy.special import comb
import math
def z_i(m, n, k, i):
    numerator = 0
    for x in range(0, k -i + 1):
        numerator += comb(m + n + 1 - i, x)

    denominator = 0
    for x in range(0, k+1):
        denominator += comb(m+n+1, x)
    return (1.0 * numerator) / denominator

def q_0(m, n, t, k):
    return ( (m + n +1)* t * (k**2) + ((-3 * n**2 + 3*m*n + 3*m + 1)*t -
             12 * (3 * m *n + m + n) - 8) * k + (-3 * m**2 + 7 * m + 10 * n +
             3 * n * m + 10) * t - 4 * (3* m * n + m + n + 1) )


def q_1(m, n, t, k):
    return (t * k**3 + 3 * (m - 1) * t * k**2 + ((-3 * n**2 + 3 * m * n - 3*m + 8)
            * t - 6 * (6 * m * n + m + n)) * k + (-3 * m**2 + 7 * (m + n) + 3*m*n)
            * t - 2 * (6 * m * n + m + n))

def get_t(m, n):
    return 3 * ((m - n)**2 + m + n) + 2


def main():
    m = 5+35.0 ## positive examples
    n = 208 + 36.0 ##negative examples
    k = 44.0

    t = get_t(m, n)
    z4 = z_i(m, n, k, 4)
    z3 = z_i(m, n, k ,3)
    z2 = z_i(m, n, k, 2)
    z1 = z_i(m, n, k, 1)

    q0 = q_0(m, n, t, k)
    q1 = q_1(m, n, t, k)

    print "t: " + str(t)
    print "z4: " + str(z4)
    print "z3: " + str(z3)
    print "z2: " + str(z2)
    print "z1: " + str(z1)

    print "q0: " + str(q0)
    print "q1: " + str(q1)

    first_numerator = (m+n+1) * (m+n)* (m + n - 1) * t * ((m+n-2)*z4 -
                      (2 * m - n + 3 * k - 10) * z3)

    first_denom = 72 * m**2 * n**2

    first_term = (first_numerator * 1.0) / first_denom


    snd_numerator = (m + n + 1)*(m+n)*t*(m**2 - n*m + 3*k*m - 5*m + 2*k**2 -
                    n*k + 12 - 9*k)*z2

    snd_denom = 48 * m**2 * n**2
    print "num: " + str(snd_numerator)
    print "denom: " + str(snd_denom)
    snd_term = (1.0 * snd_numerator) / snd_denom

    third_numerator = (m+n+1)**2 * (m-n)**4 * z1**2
    third_denom = 16 * m**2 * n**2
    third_term = (1.0 *third_numerator) / third_denom

    fourth_numerator = (m + n + 1) * q1 * z1
    fourth_denom = 72 * m**2 * n**2
    fourth_term = (1.0 * fourth_numerator) / fourth_denom 

    fifth_numerator = k * q0
    fifth_denom = 144 * m**2 * n**2
    fifth_term = (1.0 *fifth_numerator) / fifth_denom

    print first_term
    print snd_term
    print third_term
    print fourth_term
    print fifth_term
    return first_term + snd_term - third_term - fourth_term + fifth_term

print math.sqrt(main())
