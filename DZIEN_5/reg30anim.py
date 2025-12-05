import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parametry "wszechświata"
N = 201          # szerokość (liczba komórek w wierszu)
STEPS = 200      # liczba kroków w dół (czas)

# Reguła 30 zapisana jako mapa z trójek bitów na bit
rule = {
    (1,1,1): 0, (1,1,0): 0, (1,0,1): 0, (1,0,0): 1,
    (0,1,1): 1, (0,1,0): 1, (0,0,1): 1, (0,0,0): 0
}

# Siatka: czas (wiersze) x przestrzeń (kolumny)
grid = np.zeros((STEPS, N), dtype=int)

# Stan początkowy – pojedynczy "kwant" na środku
grid[0, N // 2] = 1

def compute_row(prev_row):
    """Zastosuj regułę 30 do całego wiersza."""
    N = len(prev_row)
    new_row = np.zeros_like(prev_row)
    for i in range(N):
        left  = prev_row[(i - 1) % N]
        mid   = prev_row[i]
        right = prev_row[(i + 1) % N]
        new_row[i] = rule[(left, mid, right)]
    return new_row

# Policzymy całą ewolucję z góry na dół (łatwiej animować)
for t in range(1, STEPS):
    grid[t] = compute_row(grid[t - 1])

# --- ANIMACJA ---

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_title("Emergencja – Reguła 30 (kosmiczna tkanina)")
ax.set_xlabel("Przestrzeń")
ax.set_ylabel("Czas")

# Początkowo pokazujemy tylko pierwszy wiersz
img = ax.imshow(grid*0, cmap="inferno", interpolation="nearest",
                vmin=0, vmax=1, aspect="auto")

def update(frame):
    # frame: ile wierszy pokazujemy (od 0 do STEPS-1)
    current = np.zeros_like(grid)
    current[:frame+1, :] = grid[:frame+1, :]
    img.set_data(current)
    return (img,)

anim = FuncAnimation(
    fig,
    update,
    frames=STEPS,
    interval=80,   # ms między klatkami
    blit=True
)

plt.tight_layout()
plt.show()
