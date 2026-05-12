import sys
import benchmark
import matplotlib
matplotlib.use('GTK4cairo')
import matplotlib.pyplot as plt

def main(argc: int, argv: str):
    b_times = benchmark.dct_benchmark(int(argv[1]))

    fig, ax = plt.subplots() 

    scipy_line, = ax.plot(b_times[0], label ="scipy dct2", color ="blue", linewidth = 2)
    custm_line, = ax.plot(b_times[1], label ="custom dct2", color ="red", linewidth = 2)

    fig.legend()
    ax.grid(True)
    
    plt.show()


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)