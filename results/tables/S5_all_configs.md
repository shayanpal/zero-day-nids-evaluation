### S5: mean detection over held-out families (mean ± 95% CI over 5 seeds)

| Release | Features | Model | Unseen @1% | Unseen @0.1% | Known @1% | Known @0.1% | Test FPR @0.1% |
|---|---|---|---|---|---|---|---|
| CIC-IDS2017 (original) | All features | RF | 0.452 ± 0.007 | 0.130 ± 0.024 | 0.999 ± 0.000 | 0.992 ± 0.003 | 0.0011 |
| CIC-IDS2017 (original) | All features | XGB | 0.501 ± 0.041 | 0.304 ± 0.075 | 1.000 ± 0.000 | 0.997 ± 0.003 | 0.0011 |
| CIC-IDS2017 (original) | All features | ENS | 0.464 ± 0.005 | 0.318 ± 0.082 | 1.000 ± 0.000 | 0.998 ± 0.002 | 0.0012 |
| CIC-IDS2017 (original) | All features | IF | 0.052 ± 0.026 | 0.000 ± 0.000 | 0.052 ± 0.026 | 0.000 ± 0.000 | 0.0010 |
| CIC-IDS2017 (original) | All features | CASCADE | 0.442 ± 0.015 | 0.151 ± 0.144 | 1.000 ± 0.000 | 0.969 ± 0.035 | 0.0010 |
| CIC-IDS2017 (original) | No shortcut fields | RF | 0.137 ± 0.022 | 0.057 ± 0.065 | 0.945 ± 0.004 | 0.907 ± 0.012 | 0.0010 |
| CIC-IDS2017 (original) | No shortcut fields | XGB | 0.203 ± 0.072 | 0.164 ± 0.068 | 0.947 ± 0.004 | 0.916 ± 0.006 | 0.0011 |
| CIC-IDS2017 (original) | No shortcut fields | ENS | 0.208 ± 0.075 | 0.121 ± 0.025 | 0.949 ± 0.005 | 0.918 ± 0.007 | 0.0011 |
| CIC-IDS2017 (original) | No shortcut fields | CASCADE | 0.192 ± 0.073 | 0.083 ± 0.046 | 0.931 ± 0.004 | 0.901 ± 0.014 | 0.0011 |
| CIC-IDS2017 (original) | GA (per fold) | RF | 0.358 ± 0.061 | 0.039 ± 0.029 | 1.000 ± 0.000 | 0.991 ± 0.006 | 0.0011 |
| CIC-IDS2017 (original) | GA (per fold) | XGB | 0.362 ± 0.053 | 0.051 ± 0.042 | 1.000 ± 0.000 | 0.987 ± 0.010 | 0.0011 |
| CIC-IDS2017 (original) | GA (per fold) | ENS | 0.419 ± 0.044 | 0.059 ± 0.057 | 1.000 ± 0.000 | 0.993 ± 0.008 | 0.0011 |
| CIC-IDS2017 (original) | GA (per fold) | CASCADE | 0.293 ± 0.049 | 0.021 ± 0.013 | 1.000 ± 0.001 | 0.965 ± 0.012 | 0.0010 |
| CIC-IDS2017 (original) | MI (per fold) | RF | 0.296 ± 0.058 | 0.108 ± 0.014 | 0.960 ± 0.023 | 0.847 ± 0.011 | 0.0011 |
| CIC-IDS2017 (original) | MI (per fold) | XGB | 0.271 ± 0.039 | 0.122 ± 0.034 | 0.928 ± 0.002 | 0.804 ± 0.019 | 0.0010 |
| CIC-IDS2017 (original) | MI (per fold) | ENS | 0.302 ± 0.040 | 0.108 ± 0.001 | 0.930 ± 0.001 | 0.834 ± 0.014 | 0.0010 |
| CIC-IDS2017 (original) | MI (per fold) | CASCADE | 0.239 ± 0.054 | 0.107 ± 0.001 | 0.929 ± 0.002 | 0.757 ± 0.021 | 0.0010 |
| CIC-IDS2017 (original) | RFimp (per fold) | RF | 0.329 ± 0.075 | 0.083 ± 0.058 | 0.888 ± 0.033 | 0.489 ± 0.068 | 0.0007 |
| CIC-IDS2017 (original) | RFimp (per fold) | XGB | 0.196 ± 0.039 | 0.118 ± 0.018 | 0.850 ± 0.006 | 0.767 ± 0.014 | 0.0009 |
| CIC-IDS2017 (original) | RFimp (per fold) | ENS | 0.288 ± 0.097 | 0.107 ± 0.001 | 0.864 ± 0.017 | 0.778 ± 0.018 | 0.0017 |
| CIC-IDS2017 (original) | RFimp (per fold) | CASCADE | 0.154 ± 0.071 | 0.106 ± 0.001 | 0.859 ± 0.015 | 0.727 ± 0.024 | 0.0010 |
| CIC-IDS2017 (original) | GA (saw all families) | RF | 0.603 ± 0.041 | 0.240 ± 0.119 | 1.000 ± 0.000 | 0.997 ± 0.003 | 0.0011 |
| CIC-IDS2017 (original) | GA (saw all families) | XGB | 0.555 ± 0.061 | 0.269 ± 0.083 | 1.000 ± 0.000 | 0.996 ± 0.003 | 0.0012 |
| CIC-IDS2017 (original) | GA (saw all families) | ENS | 0.633 ± 0.047 | 0.312 ± 0.050 | 1.000 ± 0.000 | 0.998 ± 0.003 | 0.0012 |
| CIC-IDS2017 (original) | GA (saw all families) | CASCADE | 0.516 ± 0.028 | 0.092 ± 0.095 | 1.000 ± 0.001 | 0.980 ± 0.015 | 0.0010 |
| CIC-IDS2017 (original) | MI (saw all families) | RF | 0.356 ± 0.017 | 0.000 ± 0.000 | 0.998 ± 0.000 | 0.128 ± 0.089 | 0.0002 |
| CIC-IDS2017 (original) | MI (saw all families) | XGB | 0.320 ± 0.063 | 0.113 ± 0.003 | 0.999 ± 0.000 | 0.794 ± 0.025 | 0.0010 |
| CIC-IDS2017 (original) | MI (saw all families) | ENS | 0.339 ± 0.037 | 0.107 ± 0.002 | 0.999 ± 0.000 | 0.816 ± 0.020 | 0.0011 |
| CIC-IDS2017 (original) | MI (saw all families) | CASCADE | 0.128 ± 0.005 | 0.107 ± 0.002 | 0.993 ± 0.005 | 0.777 ± 0.021 | 0.0011 |
| CIC-IDS2017 (original) | RFimp (saw all families) | RF | 0.197 ± 0.121 | 0.062 ± 0.051 | 0.865 ± 0.036 | 0.684 ± 0.222 | 0.0010 |
| CIC-IDS2017 (original) | RFimp (saw all families) | XGB | 0.178 ± 0.036 | 0.156 ± 0.019 | 0.798 ± 0.006 | 0.765 ± 0.014 | 0.0008 |
| CIC-IDS2017 (original) | RFimp (saw all families) | ENS | 0.180 ± 0.039 | 0.135 ± 0.019 | 0.823 ± 0.037 | 0.769 ± 0.008 | 0.0008 |
| CIC-IDS2017 (original) | RFimp (saw all families) | CASCADE | 0.187 ± 0.036 | 0.113 ± 0.019 | 0.822 ± 0.037 | 0.741 ± 0.026 | 0.0010 |
| CIC-IDS2017 (original) | Thesis GA | RF | 0.640 ± 0.016 | 0.235 ± 0.093 | 1.000 ± 0.000 | 0.996 ± 0.004 | 0.0011 |
| CIC-IDS2017 (original) | Thesis GA | XGB | 0.535 ± 0.031 | 0.263 ± 0.033 | 1.000 ± 0.000 | 0.994 ± 0.009 | 0.0011 |
| CIC-IDS2017 (original) | Thesis GA | ENS | 0.642 ± 0.008 | 0.264 ± 0.026 | 1.000 ± 0.000 | 0.996 ± 0.006 | 0.0010 |
| CIC-IDS2017 (original) | Thesis GA | CASCADE | 0.577 ± 0.010 | 0.070 ± 0.134 | 1.000 ± 0.001 | 0.978 ± 0.016 | 0.0010 |
| CIC-IDS2017 (original) | Pitfall run: clean | RF | 0.452 ± 0.007 | 0.130 ± 0.024 | 0.999 ± 0.000 | 0.992 ± 0.003 | 0.0011 |
| CIC-IDS2017 (original) | Pitfall run: clean | ENS | 0.464 ± 0.005 | 0.318 ± 0.082 | 1.000 ± 0.000 | 0.998 ± 0.002 | 0.0012 |
| CIC-IDS2017 (original) | Pitfall run: threshold on test | RF | 0.449 ± 0.011 | 0.122 ± 0.012 | 0.999 ± 0.000 | 0.992 ± 0.002 | 0.0010 |
| CIC-IDS2017 (original) | Pitfall run: threshold on test | ENS | 0.462 ± 0.004 | 0.321 ± 0.081 | 1.000 ± 0.000 | 0.999 ± 0.001 | 0.0010 |
| CIC-IDS2017 (original) | Pitfall run: no de-duplication | RF | 0.405 ± 0.093 | 0.095 ± 0.067 | 0.999 ± 0.000 | 0.988 ± 0.005 | 0.0012 |
| CIC-IDS2017 (original) | Pitfall run: no de-duplication | ENS | 0.452 ± 0.077 | 0.217 ± 0.047 | 1.000 ± 0.000 | 0.998 ± 0.002 | 0.0012 |
| CIC-IDS2017 (corrected) | All features | RF | 0.736 ± 0.109 | 0.255 ± 0.021 | 1.000 ± 0.000 | 1.000 ± 0.001 | 0.0010 |
| CIC-IDS2017 (corrected) | All features | XGB | 0.367 ± 0.054 | 0.282 ± 0.030 | 1.000 ± 0.000 | 1.000 ± 0.001 | 0.0010 |
| CIC-IDS2017 (corrected) | All features | ENS | 0.771 ± 0.108 | 0.302 ± 0.029 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.0011 |
| CIC-IDS2017 (corrected) | All features | IF | 0.040 ± 0.023 | 0.000 ± 0.000 | 0.040 ± 0.023 | 0.000 ± 0.000 | 0.0011 |
| CIC-IDS2017 (corrected) | All features | CASCADE | 0.597 ± 0.136 | 0.252 ± 0.032 | 1.000 ± 0.000 | 0.999 ± 0.002 | 0.0011 |
| CIC-IDS2017 (corrected) | No shortcut fields | RF | 0.602 ± 0.029 | 0.249 ± 0.037 | 1.000 ± 0.000 | 0.999 ± 0.002 | 0.0010 |
| CIC-IDS2017 (corrected) | No shortcut fields | XGB | 0.433 ± 0.020 | 0.235 ± 0.021 | 1.000 ± 0.000 | 1.000 ± 0.001 | 0.0010 |
| CIC-IDS2017 (corrected) | No shortcut fields | ENS | 0.595 ± 0.051 | 0.289 ± 0.040 | 1.000 ± 0.000 | 1.000 ± 0.001 | 0.0011 |
| CIC-IDS2017 (corrected) | No shortcut fields | CASCADE | 0.498 ± 0.093 | 0.229 ± 0.064 | 1.000 ± 0.000 | 0.999 ± 0.002 | 0.0011 |
| CIC-IDS2017 (corrected) | GA (per fold) | RF | 0.779 ± 0.090 | 0.477 ± 0.034 | 0.999 ± 0.001 | 0.990 ± 0.008 | 0.0010 |
| CIC-IDS2017 (corrected) | GA (per fold) | XGB | 0.545 ± 0.078 | 0.503 ± 0.007 | 0.999 ± 0.002 | 0.994 ± 0.003 | 0.0009 |
| CIC-IDS2017 (corrected) | GA (per fold) | ENS | 0.779 ± 0.147 | 0.505 ± 0.006 | 0.999 ± 0.001 | 0.994 ± 0.004 | 0.0010 |
| CIC-IDS2017 (corrected) | GA (per fold) | CASCADE | 0.628 ± 0.082 | 0.482 ± 0.020 | 0.999 ± 0.002 | 0.987 ± 0.006 | 0.0011 |
| CIC-IDS2017 (corrected) | MI (per fold) | RF | 0.331 ± 0.013 | 0.167 ± 0.000 | 0.999 ± 0.001 | 0.915 ± 0.026 | 0.0007 |
| CIC-IDS2017 (corrected) | MI (per fold) | XGB | 0.212 ± 0.033 | 0.166 ± 0.001 | 0.999 ± 0.002 | 0.902 ± 0.005 | 0.0004 |
| CIC-IDS2017 (corrected) | MI (per fold) | ENS | 0.341 ± 0.011 | 0.167 ± 0.000 | 0.999 ± 0.001 | 0.897 ± 0.004 | 0.0005 |
| CIC-IDS2017 (corrected) | MI (per fold) | CASCADE | 0.209 ± 0.036 | 0.167 ± 0.000 | 0.940 ± 0.039 | 0.895 ± 0.004 | 0.0011 |
| CIC-IDS2017 (corrected) | RFimp (per fold) | RF | 0.384 ± 0.105 | 0.174 ± 0.006 | 0.999 ± 0.001 | 0.994 ± 0.003 | 0.0009 |
| CIC-IDS2017 (corrected) | RFimp (per fold) | XGB | 0.258 ± 0.097 | 0.170 ± 0.006 | 0.999 ± 0.001 | 0.991 ± 0.003 | 0.0009 |
| CIC-IDS2017 (corrected) | RFimp (per fold) | ENS | 0.370 ± 0.095 | 0.170 ± 0.006 | 0.999 ± 0.001 | 0.994 ± 0.003 | 0.0010 |
| CIC-IDS2017 (corrected) | RFimp (per fold) | CASCADE | 0.312 ± 0.083 | 0.169 ± 0.004 | 0.999 ± 0.001 | 0.988 ± 0.007 | 0.0011 |
| CIC-IDS2017 (corrected) | GA (saw all families) | RF | 0.711 ± 0.051 | 0.319 ± 0.068 | 1.000 ± 0.000 | 0.999 ± 0.002 | 0.0008 |
| CIC-IDS2017 (corrected) | GA (saw all families) | XGB | 0.394 ± 0.041 | 0.145 ± 0.075 | 1.000 ± 0.000 | 0.999 ± 0.003 | 0.0011 |
| CIC-IDS2017 (corrected) | GA (saw all families) | ENS | 0.709 ± 0.029 | 0.308 ± 0.041 | 1.000 ± 0.000 | 0.999 ± 0.002 | 0.0009 |
| CIC-IDS2017 (corrected) | GA (saw all families) | CASCADE | 0.654 ± 0.059 | 0.156 ± 0.068 | 1.000 ± 0.000 | 0.999 ± 0.003 | 0.0011 |
| CIC-IDS2017 (corrected) | MI (saw all families) | RF | 0.412 ± 0.087 | 0.223 ± 0.020 | 1.000 ± 0.000 | 0.996 ± 0.004 | 0.0009 |
| CIC-IDS2017 (corrected) | MI (saw all families) | XGB | 0.236 ± 0.036 | 0.179 ± 0.019 | 1.000 ± 0.000 | 0.998 ± 0.002 | 0.0005 |
| CIC-IDS2017 (corrected) | MI (saw all families) | ENS | 0.391 ± 0.024 | 0.228 ± 0.034 | 1.000 ± 0.000 | 0.998 ± 0.002 | 0.0009 |
| CIC-IDS2017 (corrected) | MI (saw all families) | CASCADE | 0.359 ± 0.017 | 0.203 ± 0.026 | 1.000 ± 0.001 | 0.998 ± 0.003 | 0.0011 |
| CIC-IDS2017 (corrected) | RFimp (saw all families) | RF | 0.657 ± 0.062 | 0.216 ± 0.028 | 1.000 ± 0.000 | 0.998 ± 0.004 | 0.0009 |
| CIC-IDS2017 (corrected) | RFimp (saw all families) | XGB | 0.536 ± 0.167 | 0.189 ± 0.006 | 1.000 ± 0.000 | 1.000 ± 0.001 | 0.0010 |
| CIC-IDS2017 (corrected) | RFimp (saw all families) | ENS | 0.674 ± 0.089 | 0.216 ± 0.036 | 1.000 ± 0.000 | 0.999 ± 0.001 | 0.0010 |
| CIC-IDS2017 (corrected) | RFimp (saw all families) | CASCADE | 0.579 ± 0.073 | 0.178 ± 0.007 | 1.000 ± 0.000 | 0.996 ± 0.003 | 0.0011 |
| CSE-CIC-IDS2018 (original) | All features | RF | 0.515 ± 0.109 | 0.091 ± 0.015 | 0.999 ± 0.001 | 0.993 ± 0.002 | 0.0011 |
| CSE-CIC-IDS2018 (original) | All features | XGB | 0.541 ± 0.090 | 0.236 ± 0.158 | 0.999 ± 0.000 | 0.996 ± 0.001 | 0.0010 |
| CSE-CIC-IDS2018 (original) | All features | ENS | 0.571 ± 0.124 | 0.192 ± 0.111 | 0.999 ± 0.000 | 0.997 ± 0.001 | 0.0010 |
| CSE-CIC-IDS2018 (original) | All features | IF | 0.079 ± 0.017 | 0.000 ± 0.000 | 0.079 ± 0.017 | 0.000 ± 0.000 | 0.0010 |
| CSE-CIC-IDS2018 (original) | All features | CASCADE | 0.506 ± 0.180 | 0.124 ± 0.091 | 0.999 ± 0.000 | 0.995 ± 0.001 | 0.0010 |
| CSE-CIC-IDS2018 (original) | No shortcut fields | RF | 0.191 ± 0.014 | 0.000 ± 0.000 | 0.956 ± 0.007 | 0.254 ± 0.198 | 0.0003 |
| CSE-CIC-IDS2018 (original) | No shortcut fields | XGB | 0.136 ± 0.120 | 0.012 ± 0.006 | 0.958 ± 0.008 | 0.902 ± 0.015 | 0.0010 |
| CSE-CIC-IDS2018 (original) | No shortcut fields | ENS | 0.246 ± 0.130 | 0.002 ± 0.003 | 0.961 ± 0.008 | 0.904 ± 0.013 | 0.0010 |
| CSE-CIC-IDS2018 (original) | No shortcut fields | CASCADE | 0.117 ± 0.029 | 0.000 ± 0.000 | 0.950 ± 0.009 | 0.889 ± 0.014 | 0.0011 |
| CSE-CIC-IDS2018 (original) | GA (per fold) | RF | 0.592 ± 0.135 | 0.296 ± 0.088 | 0.999 ± 0.001 | 0.996 ± 0.002 | 0.0010 |
| CSE-CIC-IDS2018 (original) | GA (per fold) | XGB | 0.529 ± 0.062 | 0.288 ± 0.094 | 0.999 ± 0.001 | 0.994 ± 0.002 | 0.0010 |
| CSE-CIC-IDS2018 (original) | GA (per fold) | ENS | 0.685 ± 0.031 | 0.289 ± 0.117 | 0.999 ± 0.000 | 0.996 ± 0.002 | 0.0010 |
| CSE-CIC-IDS2018 (original) | GA (per fold) | CASCADE | 0.626 ± 0.100 | 0.189 ± 0.129 | 0.998 ± 0.000 | 0.994 ± 0.002 | 0.0011 |
| CSE-CIC-IDS2018 (original) | MI (per fold) | RF | 0.255 ± 0.088 | 0.106 ± 0.091 | 0.878 ± 0.016 | 0.691 ± 0.014 | 0.0005 |
| CSE-CIC-IDS2018 (original) | MI (per fold) | XGB | 0.171 ± 0.004 | 0.101 ± 0.017 | 0.873 ± 0.008 | 0.828 ± 0.017 | 0.0007 |
| CSE-CIC-IDS2018 (original) | MI (per fold) | ENS | 0.215 ± 0.006 | 0.085 ± 0.027 | 0.877 ± 0.007 | 0.836 ± 0.010 | 0.0007 |
| CSE-CIC-IDS2018 (original) | MI (per fold) | CASCADE | 0.270 ± 0.030 | 0.067 ± 0.007 | 0.870 ± 0.004 | 0.824 ± 0.015 | 0.0011 |
| CSE-CIC-IDS2018 (original) | RFimp (per fold) | RF | 0.672 ± 0.149 | 0.225 ± 0.134 | 0.998 ± 0.001 | 0.994 ± 0.003 | 0.0011 |
| CSE-CIC-IDS2018 (original) | RFimp (per fold) | XGB | 0.343 ± 0.148 | 0.221 ± 0.062 | 0.999 ± 0.000 | 0.994 ± 0.002 | 0.0010 |
| CSE-CIC-IDS2018 (original) | RFimp (per fold) | ENS | 0.535 ± 0.111 | 0.201 ± 0.112 | 0.999 ± 0.001 | 0.995 ± 0.002 | 0.0011 |
| CSE-CIC-IDS2018 (original) | RFimp (per fold) | CASCADE | 0.486 ± 0.133 | 0.096 ± 0.020 | 0.998 ± 0.000 | 0.993 ± 0.003 | 0.0011 |
| CSE-CIC-IDS2018 (original) | GA (saw all families) | RF | 0.704 ± 0.018 | 0.309 ± 0.067 | 0.998 ± 0.001 | 0.996 ± 0.001 | 0.0009 |
| CSE-CIC-IDS2018 (original) | GA (saw all families) | XGB | 0.614 ± 0.025 | 0.247 ± 0.124 | 0.999 ± 0.001 | 0.993 ± 0.002 | 0.0010 |
| CSE-CIC-IDS2018 (original) | GA (saw all families) | ENS | 0.698 ± 0.010 | 0.280 ± 0.119 | 0.999 ± 0.001 | 0.995 ± 0.002 | 0.0010 |
| CSE-CIC-IDS2018 (original) | GA (saw all families) | CASCADE | 0.701 ± 0.026 | 0.176 ± 0.038 | 0.998 ± 0.001 | 0.993 ± 0.002 | 0.0011 |
| CSE-CIC-IDS2018 (original) | MI (saw all families) | RF | 0.108 ± 0.078 | 0.108 ± 0.078 | 0.761 ± 0.070 | 0.761 ± 0.070 | 0.0284 |
| CSE-CIC-IDS2018 (original) | MI (saw all families) | XGB | 0.135 ± 0.041 | 0.135 ± 0.041 | 0.704 ± 0.011 | 0.704 ± 0.011 | 0.0006 |
| CSE-CIC-IDS2018 (original) | MI (saw all families) | ENS | 0.149 ± 0.061 | 0.149 ± 0.061 | 0.711 ± 0.026 | 0.711 ± 0.026 | 0.0098 |
| CSE-CIC-IDS2018 (original) | MI (saw all families) | CASCADE | 0.224 ± 0.060 | 0.124 ± 0.074 | 0.711 ± 0.026 | 0.685 ± 0.023 | 0.0102 |
| CSE-CIC-IDS2018 (original) | RFimp (saw all families) | RF | 0.643 ± 0.048 | 0.096 ± 0.041 | 0.998 ± 0.001 | 0.993 ± 0.002 | 0.0010 |
| CSE-CIC-IDS2018 (original) | RFimp (saw all families) | XGB | 0.364 ± 0.101 | 0.180 ± 0.158 | 0.998 ± 0.001 | 0.993 ± 0.002 | 0.0011 |
| CSE-CIC-IDS2018 (original) | RFimp (saw all families) | ENS | 0.628 ± 0.147 | 0.180 ± 0.127 | 0.999 ± 0.001 | 0.994 ± 0.002 | 0.0011 |
| CSE-CIC-IDS2018 (original) | RFimp (saw all families) | CASCADE | 0.517 ± 0.111 | 0.046 ± 0.019 | 0.997 ± 0.001 | 0.992 ± 0.003 | 0.0011 |
| CSE-CIC-IDS2018 (original) | Pitfall run: clean | RF | 0.515 ± 0.109 | 0.091 ± 0.015 | 0.999 ± 0.001 | 0.993 ± 0.002 | 0.0011 |
| CSE-CIC-IDS2018 (original) | Pitfall run: clean | ENS | 0.571 ± 0.124 | 0.192 ± 0.111 | 0.999 ± 0.000 | 0.997 ± 0.001 | 0.0010 |
| CSE-CIC-IDS2018 (original) | Pitfall run: threshold on test | RF | 0.521 ± 0.117 | 0.081 ± 0.015 | 0.999 ± 0.001 | 0.992 ± 0.003 | 0.0010 |
| CSE-CIC-IDS2018 (original) | Pitfall run: threshold on test | ENS | 0.573 ± 0.153 | 0.237 ± 0.145 | 0.999 ± 0.000 | 0.997 ± 0.001 | 0.0010 |
| CSE-CIC-IDS2018 (original) | Pitfall run: no de-duplication | RF | 0.638 ± 0.053 | 0.181 ± 0.024 | 0.998 ± 0.001 | 0.987 ± 0.005 | 0.0010 |
| CSE-CIC-IDS2018 (original) | Pitfall run: no de-duplication | ENS | 0.676 ± 0.052 | 0.282 ± 0.049 | 0.999 ± 0.001 | 0.996 ± 0.002 | 0.0011 |
