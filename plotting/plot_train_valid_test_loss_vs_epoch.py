import os
import re
import argparse
import matplotlib.pyplot as plt

epoch_pattern = epoch_pattern = r"(?:.|\n)*?epoch (\d+), training loss ([\d.]+) \(\d+.\d+ sec\)(?:, valid loss ([\d.]+), test loss ([\d.]+))?"

def parse_log_file(file_path):
    losses = {"train_loss": {}, "valid_loss": {}, "test_loss": {}}
    with open(file_path, 'r') as file:
        log_text = file.read()
        matches = re.findall(epoch_pattern, log_text)
        for match in matches:
            epoch, train_loss, valid_loss, test_loss = match
            epoch = int(epoch)
            losses["train_loss"][epoch] = float(train_loss)
            if valid_loss and test_loss:
                losses["valid_loss"][epoch] = float(valid_loss)
                losses["test_loss"][epoch] = float(test_loss)
    return losses

def print_losses(losses, log_file):
    print(f"\n{log_file} - Losses by Epoch:")
    
    print("Train Loss:")
    for epoch, value in sorted(losses["train_loss"].items()):
        print(f"Epoch {epoch}: {value}")
    
    print("Valid Loss:")
    for epoch, value in sorted(losses["valid_loss"].items()):
        print(f"Epoch {epoch}: {value}")
    
    print("Test Loss:")
    for epoch, value in sorted(losses["test_loss"].items()):
        print(f"Epoch {epoch}: {value}")

def plot_losses(log_files, losses_data, loss_type, x_lim=None, y_lim=None):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for log_file, losses in zip(log_files, losses_data):
        data = losses[loss_type]
        epochs_list = sorted(data.keys())
        values = [data[epoch] for epoch in epochs_list]
        if values:
            log_name = os.path.splitext(log_file)[0]
            ax.plot(epochs_list, values, label=log_name)

            ax.annotate(log_file,
                        xy=(epochs_list[-1], values[-1]),
                        xytext=(5, 0), 
                        textcoords='offset points',
                        fontsize=10,
                        color=ax.get_lines()[-1].get_color()) 

    if x_lim:
        ax.set_xlim(x_lim)
    if y_lim:
        ax.set_ylim(y_lim)

    ax.set_xlabel('Epochs')
    ax.set_ylabel(f'{loss_type.capitalize()} Loss')
    ax.set_title(f'{loss_type.capitalize()} Loss Comparison Across Methods')
    ax.legend()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare training, validation, and test loss across multiple logs.")
    parser.add_argument("--compare", nargs='+', required=True, help="Log files to compare.")
    parser.add_argument("--x_lim", nargs=2, type=float, help="Set x-axis limits as two float values: min and max.")
    parser.add_argument("--y_lim", nargs=2, type=float, help="Set y-axis limits as two float values: min and max.")
    parser.add_argument("--epochs", type=int, default=200, help="Set the number of epochs for plotting.")
    
    args = parser.parse_args()

    log_files = args.compare
    x_lim = tuple(args.x_lim) if args.x_lim else None
    y_lim = tuple(args.y_lim) if args.y_lim else None

    losses_data = []
    for log_file in log_files:
        losses = parse_log_file(log_file)
        print_losses(losses, log_file)
        losses_data.append(losses)

    for loss_type in ['train_loss', 'valid_loss', 'test_loss']:
        plot_losses(log_files, losses_data, loss_type, x_lim=x_lim, y_lim=y_lim)