import matplotlib.pyplot as plt
import seaborn as sns


def configure_plotting():
    sns.set_theme(style = 'whitegrid')
    plt.rcParams.update(
        {
            'font.family': 'DejaVu Sans',
            'figure.max_open_warning': 0,
            'grid.color': '#D8E0E3',
            'grid.linewidth': 0.65,
            'grid.alpha': 0.7,
        }
    )
