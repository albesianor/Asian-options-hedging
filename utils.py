# Utils module for Erdos's quant finance bootcamp
import numpy as np
from scipy.stats import norm, gmean


# Analytic pricers
# - Black-Scholes
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
        raise ValueError("Unrecognized option type: {}".format(option_type))


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
        raise ValueError("Unrecognized option type: {}".format(option_type))

# Geometric Asian option
def gao_price(S0, K, sigma, t, r, option_type='call'):
    '''Geometric Asian option pricer
    Inputs:
    S0 (float): Stock price at time 0
    K (float): Strike Price
    sigma: Yearly volatility
    t: Time to expiration (years)
    r: Risk-free Interest rate

    Return:
    Computed value of a geometric Asian call/put option (float)
    '''
    b = (r - sigma**2 / 6) / 2
    d1 = np.sqrt(3)*(np.log(S0/K) + (b + sigma**2 / 6)*t) / (sigma * np.sqrt(t))
    d2 = d1 - sigma * np.sqrt(t/3)

    if option_type == 'put':
        return K * np.exp(-r*t) * norm.cdf(-d2) - S0 * np.exp((b-r)*t) * norm.cdf(-d1)
    elif option_type == 'call':
        return S0 * np.exp((b-r)*t) * norm.cdf(d1) - K * np.exp(-r*t) * norm.cdf(d2)
    else:
        raise ValueError("Unrecognized option type: {}".format(option_type))


# Monte Carlo methods
# - stock paths generator
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

# - European options
def monte_carlo_european(S0, K, sigma, t, r, mu, n_sims, n_hedges, return_distribution=True, option_type='call'):
    """Monte-Carlo simulation of a European option value with Black-Scholes assumptions with delta hedging.

    Inputs:
    S0 (float): underlying stock price at time 0
    K (float): strike price
    sigma (float): yearly volatility
    t (float): time to expiration (years)
    r (float): risk-free interest rate
    mu (float): drift of log-returns
    n_sims (int): number of simulated paths
    n_hedges (int): number of delta-hedges
    
    Returns:
    If return_distribution is true, returns distribution of simulated call values with delta hedging;
      if false, returns the average payoff and standard deviation of call option with delta hedging

    To simulate the profit distribution of selling n_options number of call options for a premimum, run
    n_options*(premium - bs_MC_call(S0, K, sigma, t, r, mu, n_sims, n_hedges) - tr_cost*n_hedges)
    
    """
    if n_hedges == 0:
        paths = GBM_paths(S0, sigma, t, r, mu, n_sims, n_steps=1)
        S_t = paths[:, -1]  # Terminal prices

        if option_type == 'call':
            discounted_payoff = np.exp(-r * t) * np.maximum(S_t - K, 0)
        elif option_type == 'put':
            discounted_payoff = np.exp(-r * t) * np.maximum(K - S_t, 0)
        else:
            raise ValueError("Unrecognized option type: {}".format(option_type))

        if return_distribution:
            return discounted_payoff
        else:
            return np.mean(discounted_payoff), np.std(discounted_payoff)/np.sqrt(n_sims)

    else:
        paths = GBM_paths(S0, sigma, t, r, mu, n_sims, n_hedges)
        S_t = paths[:, -1]  # Terminal prices

        if option_type == 'call':
            discounted_payoff = np.exp(-r * t) * np.maximum(S_t - K, 0)
        elif option_type == 'put':
            discounted_payoff = np.exp(-r * t) * np.maximum(K - S_t, 0)
        else:
            raise ValueError("Unrecognized option type: {}".format(option_type))

        times = np.linspace(0, t, n_hedges + 1)

        deltas = bs_delta(paths[:,0:n_hedges], K, sigma, (t-times)[0:n_hedges], r, option_type=option_type)

        stock_profits_discounted = (paths[:,1:n_hedges + 1] - \
                                    paths[:,0:n_hedges]*np.exp(r*t/n_hedges))*np.exp(-r*times[1:n_hedges+1])*deltas

        profit_with_hedging = discounted_payoff - np.sum(stock_profits_discounted, axis=1)

        if return_distribution:
            return profit_with_hedging
        else:
            return np.mean(profit_with_hedging), np.std(profit_with_hedging)/np.sqrt(n_sims)

# - Asian options
def monte_carlo_gao(S0, K, sigma, t, r, mu, n_sims, n_steps, geometric=False, return_distribution=True, option_type="call"):
    """
    S0 (float): Underlying stock price at time 0
    sigma (float): Yearly volatility
    t (float): Time to expiration (years)
    r (float): Risk-free interest rate
    mu (float): Drift of log-returns
    n_sims (int): Number of simulated paths
    n_steps (int): Number of steps in the average

    Returns:
    If return_distribution is true, returns distribution of simulated values;
      if false, returns the average payoff of option
    """
    paths = GBM_paths(S0, sigma, t, r, mu, n_sims, n_steps)
    if geometric:
        S = gmean(paths, axis=1)  # geometric mean of prices
    else:
        S = np.mean(paths, axis=1)  # arithmetic mean of prices

    if option_type == "call":
        discounted_payoff = np.exp(-r * t) * np.maximum(S - K, 0)
    elif option_type == "put":
        discounted_payoff = np.exp(-r * t) * np.maximum(K - S, 0)
    else:
        raise ValueError("Unrecognized option type: {}".format(option_type))

    if return_distribution:
        return discounted_payoff
    else:
        return np.mean(discounted_payoff)