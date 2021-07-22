N1 = 9000

N2 = 5000

N = N1 + N2

k = 2

mu_samples_1_1 = 58.
mu_samples_1_2 = 19.

mu_samples_2_1 = 49.
mu_samples_2_2 = 7.5

sigma_samples_1_1 = 2.5
sigma_samples_1_2 = 0.9

sigma_samples_2_1 = 2.1
sigma_samples_2_2 = 0.82


def e_step(x, k, m, n, w, mu, sigma):

    pj_xi = []
    for j in range(k):
        det_sigma_j = np.linalg.det(sigma[j])
        factor_1 = 1 / (((2 * math.pi)**(k/2)) * ((det_sigma_j)**0.5))
        factor_2 = []
        for i in x:
            factor_2.append(math.e**float(
                -0.5 * np.matrix(i - mu[j]) * np.matrix(np.linalg.inv(sigma[j])) * np.matrix(i - mu[j]).T))
        pj_xi.append(factor_1 * np.array(factor_2))
    pj_xi = np.array(pj_xi)
    

    pj_xi_w = []
    for j in range(k):
        pj_xi_w.append(pj_xi[j] * w[j])
    pj_xi_w = np.array(pj_xi_w)
    

    sum_pj_xi_w = np.sum(pj_xi_w, axis = 0)
    

    proba_xi = []
    for j in range(k):
        proba_xi.append(pj_xi_w[j] / sum_pj_xi_w)
    
    return np.array(proba_xi)


def x_new(proba_xi):
    X1_new_ind = []
    X2_new_ind = []
    X_answers = []

    count = 0
    for x in proba_xi[0]:
        if x >= 0.5:
            X1_new_ind.append(count)
            X_answers.append(1)
        else:
            X2_new_ind.append(count)
            X_answers.append(2)
        count += 1

    return X1_new_ind, X2_new_ind, X_answers


def m_step(x, proba_xi,N):
    w_new = np.sum(proba_xi, axis = 1) / N
    
    mu_new = (np.array((np.matrix(proba_xi) * np.matrix(X))).T / np.sum(proba_xi, axis = 1)).T
    
    cov_new = []
    for mu in range(mu_new.shape[0]):
        X_cd = []
        X_cd_proba = []
        count = 0
        for x_i in x:
            cd = np.array(x_i - mu_new[mu])
            X_cd.append(cd)
            X_cd_proba.append(cd * proba_xi[mu][count])
            count += 1
        X_cd = np.array(X_cd)
        X_cd = X_cd.reshape(N, m)
        X_cd_proba = np.array(X_cd_proba)
        X_cd_proba = X_cd_proba.reshape(N, m)

        cov_new.append(np.matrix(X_cd.T) * np.matrix(X_cd_proba))
    cov_new = np.array((np.array(cov_new) / (np.sum(proba_xi, axis = 1)-1)))

    if cov_new[0][0][1] < 0:
        cov_new[0][0][1] = 0
    if cov_new[0][1][0] < 0:
        cov_new[0][1][0] = 0
    
    if cov_new[1][0][1] < 0:
        cov_new[1][0][1] = 0
    if cov_new[1][1][0] < 0:
        cov_new[1][1][0] = 0
    
    sigma_new = cov_new**0.5
    return w_new, mu_new, sigma_new
    
X = np.zeros((N, 2))

np.random.seed(seed=000)
X[:N1, 0] = np.random.normal(loc=mu_samples_1_1, scale=sigma_samples_1_1, size=N1)
X[:N1, 1] = np.random.normal(loc=mu_samples_1_2, scale=sigma_samples_1_2, size=N1)

X[N1:N, 0] = np.random.normal(loc=mu_samples_2_1, scale=sigma_samples_2_1, size=N2)
X[N1:N, 1] = np.random.normal(loc=mu_samples_2_2, scale=sigma_samples_2_2, size=N2)

m = X.shape[1]

n = X.shape[0]

y = np.zeros((N))
y[:N1] = np.array((1))
y[N1:N] = np.array((2))

w = np.array([float(1./k), float(1./k)])

np.random.seed(seed = None)
mu  = np.array(
    (np.mean(X[np.random.choice(n, n/k)], axis = 0), np.mean(X[np.random.choice(n, n/k)], axis = 0)))
# mu = np.array(([mu_samples_1_1, mu_samples_1_2],[mu_samples_2_1, mu_samples_2_2]))


sigma = np.array(([1., 0.],[0., 1.], [1., 0.],[0., 1.]))
# sigma = np.array(([sigma_samples_1_1, 0.],[0., sigma_samples_1_2], [sigma_samples_2_1, 0.],[0., sigma_samples_2_2]))
sigma = sigma.reshape(k, m, m)


steps = 15

for i in range(steps):
    proba_xi = e_step(X, k, m, n, w, mu, sigma)
    w, mu, sigma = m_step(X, proba_xi,N)
    X1_new_ind, X2_new_ind, X_answers = x_new(proba_xi)
    print 'Iteration', i+1
    print
    print 'mu:'
    print mu
    print
    print 'sigma:'
    print sigma
    print
    print 'Checking step:'
    print round(accuracy_score(y, X_answers),3)
    
    plt.figure(figsize=(16, 6))  
    plt.plot(
        X[X1_new_ind,0], X[X1_new_ind,1], 'o', alpha = 0.7, color='sandybrown', label = '#1')
    plt.plot(
        X[X2_new_ind,0], X[X2_new_ind,1], 'o', alpha = 0.45, color = 'darkblue', label = '#2')
    plt.plot(mu[0][0], mu[0][1], 'o', markersize = 16, color = 'red', label = 'Mu 1')
    plt.plot(mu[1][0], mu[1][1], 'o',  markersize = 16, color = 'purple', label = 'Mu 2')
    plt.xlabel('Diameter')
    plt.ylabel('Weight')
    plt.legend()
    plt.show()