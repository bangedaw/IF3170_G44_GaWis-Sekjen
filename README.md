# Mejiro Express: Local Search untuk Pengisian Peti Kemas

Tugas Besar 1 IF3170 Inteligensi Artifisial 2026/2027.

Program ini mencari konfigurasi pengisian paket paling optimal pada peti kemas truk, yaitu memaksimalkan total *value* paket yang diangkut tanpa melanggar constraint. Pencarian memakai algoritma *local search*: Hill-climbing (beberapa varian), Simulated Annealing, dan Genetic Algorithm.

## Constraint dan objective
- Paket berbentuk balok, koordinat bilangan bulat, dan enam kemungkinan orientasi.
- Paket tidak boleh menembus dinding peti kemas atau saling tumpang-tindih.
- Paket tidak boleh melayang: minimal satu titik alasnya harus tersangga (lantai atau sisi atas paket lain).
- Paket pecah-belah (*fragile*) tidak boleh menjadi penyangga.
- Total berat per truk tidak boleh melebihi kapasitas.
- Objective default adalah total *value* paket di dalam truk. State yang melanggar constraint tetap boleh dikunjungi pencarian tetapi dikenai penalti.

Bonus yang dikerjakan: objective alternatif `alt` (Bonus 1), seluruh varian Hill-climbing (Bonus 2), dan multi-truk (Bonus 3).

## Setup
Membutuhkan Python 3.11 atau lebih baru.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Semua perintah di bawah dijalankan dari root repository.

## Cara menjalankan

### Satu algoritma pada satu problem
```bash
python src/main.py --list                      # daftar algoritma dan alias
python src/main.py --problem src/data/medium.json --algo ga --seed 1 --out output/manual
```
Opsi: `--objective default|alt`, `--params '{"population_size": 30, "generations": 40}'` atau `--param key=value` (boleh diulang), `--label`, `--out` (file `.json` atau folder).

### Problem uji
| File | Isi |
|---|---|
| `src/data/small.json` | 1 truk, 10 paket |
| `src/data/medium.json` | 1 truk (10x20x5, kapasitas 500), 35 paket. Dipakai untuk semua eksperimen wajib |
| `src/data/large.json` | 1 truk, 56 paket |
| `src/data/multi_truck.json` | 3 truk, 52 paket (Bonus 3) |

Keempat file di atas dapat dibuat ulang secara deterministik dengan `PYTHONPATH=src python -m core.generator`.

### Satu set eksperimen dari file konfigurasi
```bash
python src/experiments/run_experiments.py src/experiments/configs/ga.json
python src/experiments/run_experiments.py src/experiments/configs/bonus_objective.json src/experiments/configs/bonus_multi_truck.json
```
Opsi: `--dry-run` (hanya menampilkan daftar run), `--skip-existing`, `--only TEKS`. Setiap run disimpan sebagai satu file JSON di `output/<eksperimen>/`. Konfigurasi memakai seed 1, 2, 3.

### Rekap hasil
```bash
python src/experiments/summarize.py --output-dir output/genetic_algorithm
```
Menghasilkan rekap per run dan per konfigurasi (rata-rata dan standar deviasi) dalam CSV dan Markdown.

### Plot
```bash
PYTHONPATH=src python -m visualization.plots output/genetic_algorithm   # PNG ke output/genetic_algorithm/plots/
```
Menghasilkan plot objective terhadap iterasi, e^(ΔE/T) (Simulated Annealing), objective maksimum dan rata-rata populasi (Genetic Algorithm), dan perbandingan antar-run.

### Visualisasi state dan hasil eksperimen
```bash
python src/visualization/app.py output --port 8501
```
Membuka viewer web di `http://127.0.0.1:8501`: *initial* dan *final state* (paket di dalam dan di luar truk, per truk untuk multi-truk), metrik run, dan plot. Gunakan `--no-browser` untuk tidak membuka browser otomatis.

### Tes
```bash
python -m pytest src/tests -q
```

## Struktur repository
```
src/
  main.py                 CLI satu algoritma
  core/                   model data, orientasi, constraint, objective, moves, initializer, generator
  algorithms/             LocalSearch (base), registry, hill_climbing/, simulated_annealing.py, genetic_algorithm.py
  experiments/            runner, rekap hasil, configs/
  visualization/          plots.py (grafik), state_view.py dan app.py (viewer)
  data/                   problem uji
  tests/                  tes dan fixture
output/                   hasil run (JSON, PNG, rekap)
docs/                     laporan (PDF)
```

## Heuristik pada core
- **Kandidat koordinat:** posisi paket dibatasi ke titik yang bersentuhan dengan dinding atau paket lain (*extreme points*), lalu paket "dijatuhkan" ke penyangga tertingginya, sehingga neighborhood tetap terkendali dan hampir selalu valid.
- **Gravity settle:** saat sebuah paket diangkat atau dirotasi, paket yang bertumpu padanya dijatuhkan agar satu move tidak memunculkan banyak pelanggaran "melayang".
- **Penalti:** tiap pelanggaran dihukum sebesar skor paket terbesar, dan kelebihan berat dihukum sebanding rasio skor per berat terbesar.

## Pembagian tugas
| Nama | NIM | Tanggung jawab |
|---|---|--|
| Edward David Rumahorbo | 1352436 | *Core engine* (model data, constraint, objective termasuk Bonus 1, neighbor moves, initial state, multi-truk di core, generator dan data uji), modul plot, README |
| Miguel Rangga Deardo Sinaga | 13524069 | Kelas dasar algoritma dan format hasil run, seluruh varian Hill-climbing (Bonus 2), Simulated Annealing, CLI `main.py`, experiment runner, rekap hasil |
| Reysha Syafitri Mulya Ramadhan | 13524137 | Genetic Algorithm, visualisasi 3D state, aplikasi viewer hasil eksperimen |
