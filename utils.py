# Utils module for Erdos's quant finance bootcamp
import numpy as np
from scipy.stats import norm


# Black-Scholes pricers

def bs_price(S0, K, sigma, t, r, option_type='call'):
    '''
    Black-Scholes Call Option formula

    Inputs:
    S0 (float): Stock price at time 0
    K (float): Strike Price
    sigma: Yearly volatility
    t: Time to expiration (years)
    r: Risk-free Interest rate


    Return:
    Black-Scholes value of call/put option (float)
    '''

    d1 = (np.log(S0/K) + (r + (0.5)*sigma**2)*t)/(sigma*np.sqrt(t))
    d2 = d1 - sigma*np.sqrt(t)
    
    if option_type == 'put':
        return -S0*norm.cdf(-d1) + K*np.exp(-r*t)*norm.cdf(-d2)
    elif option_type == 'call':
        return S0*norm.cdf(d1) - K*np.exp(-r*t)*norm.cdf(d2)
    else:
        print("Unrecognized option type:", option_type)


def bs_delta(S0, K, sigma, t, r, option_type='call'):
    '''Black-Scholes Delta of Call Option
    
    Inputs:
    S0 (float): Stock price at time 0
    K (float): Strike Price
    sigma: Yearly volatility
    t: Time to expiration (years)
    r: Risk-free Interest rate
    
    
    Return:
    Black-Scholes rate of change of call/put option with respect to S_0
    '''

    d1 = (np.log(S0/K) + (r + (0.5)*sigma**2)*t)/(sigma*np.sqrt(t))

    if option_type == 'put':
        return norm.cdf(d1) - 1
    elif option_type == 'call':
        return norm.cdf(d1)
    else:
        print("Unrecognized option type:", option_type)


# Monte Carlo methods
def GBM_paths(S0, sigma, t, r, mu, n_sims, n_steps):
    """Simulates stock paths as geometric Brownian Motions
    Inputs:
    S0 (float): Underlying stock price at time 0
    sigma (float): Yearly volatility
    t (float): Time to expiration (years)
    r (float): Risk-free interest rate
    mu (float): Drift of log-returns
    n_sims (int): Number of simulated paths
    n_steps (int): Number of steps in each simulated path, each step interval has length t/n_steps
    
    Return (np.array): Array of stock paths
    """
    
    noise = np.random.normal(loc = 0, scale = 1, size = (n_sims, n_steps))
    log_returns = (mu+r-sigma**2*(0.5))*t/n_steps + sigma*np.sqrt(t/n_steps)*noise
    paths_with_start = np.insert(S0*np.exp(np.cumsum(log_returns, axis = 1)), 0, S0, axis = 1)

    return paths_with_start

