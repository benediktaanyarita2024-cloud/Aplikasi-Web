import pandas as pd
import streamlit as st

# Mengatur judul aplikasi dashboard
st.title("☄️ Dashboard Analisis Meteorit Jatuh Global")

# Mendefinisikan URL sumber dataset CSV meteorit global (NASA / The Meteoritical Society)
DATA_URL = (
    "https://raw.githubusercontent.com/bcdunbar/datasets/master/meteorites_subset.csv"
)


# Decorator untuk menyimpan hasil komputasi fungsi di memori cache Streamlit
@st.cache_data
def load_data():
    # 1. Membaca dataset CSV dari URL (encoding latin1 karena ada karakter non-UTF8 pada nama meteorit)
    df = pd.read_csv(DATA_URL, encoding="latin1")

    # 2. Konversi kolom "year" ke format datetime
    df["year"] = pd.to_datetime(df["year"], errors="coerce")

    # 3. Mengubah nama kolom "reclat" -> "lat" dan "reclong" -> "lon" agar sesuai dengan st.map()
    df.rename(columns={"reclat": "lat", "reclong": "lon"}, inplace=True)

    # 4. Membuang baris dengan tanggal tidak valid dan koordinat (0,0) yang invalid
    df = df.dropna(subset=["year", "lat", "lon", "mass (g)"])
    df = df[(df["lat"] != 0) | (df["lon"] != 0)]

    # 5. Mengonversi massa dari gram ke kilogram agar angka lebih ringkas (tidak terlalu banyak angka 0)
    df["mass_kg"] = df["mass (g)"] / 1000

    return df


data_load_state = st.text("Memuat data...")
df = load_data()
data_load_state.text("Data berhasil dimuat! (menggunakan st.cache_data)")

# Menampilkan subheader/judul bagian
st.subheader("📌 Ringkasan Statistik Meteorit")

# Membuat tata letak 3 kolom sejajar
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Meteorit Tercatat", value=f"{len(df):,}")

with col2:
    st.metric(label="Rata-rata Massa", value=f"{df['mass_kg'].mean():,.2f} kg")

with col3:
    st.metric(label="Massa Terberat", value=f"{df['mass_kg'].max():,.1f} kg")

st.divider()

# Menampilkan judul sub-bagian filter
st.subheader("⚙️ Filter Data Meteorit")

# Slider filter berdasarkan rentang massa dalam KILOGRAM
# (dipilih kg, bukan gram, supaya rentang nilainya tidak berderet angka nol)
min_mass, max_mass = st.slider(
    label="Pilih Rentang Massa (kg):",
    min_value=float(df["mass_kg"].min()),
    max_value=float(df["mass_kg"].max()),
    value=(0.001, 50.0),
)

# Menyaring (filter) dataset berdasarkan rentang massa yang dipilih pada slider
filtered_data = df[
    (df["mass_kg"] >= min_mass) & (df["mass_kg"] <= max_mass)
]

# Menampilkan judul bagian grafik
st.subheader("📈 Tren Kejadian Meteorit Jatuh per Tahun")

# Mengelompokkan data terfilter berdasarkan tahun dan menghitung jumlah kejadian
df_year = (
    filtered_data.groupby(filtered_data["year"].dt.year)
    .size()
    .reset_index(name="Jumlah Meteorit")
)
df_year.rename(columns={"year": "Tahun"}, inplace=True)

st.line_chart(df_year, x="Tahun", y="Jumlah Meteorit")

# Menampilkan judul bagian peta dilengkapi dengan jumlah titik yang terdeteksi secara dinamis
st.subheader(f"🗺️ Peta Sebaran Meteorit ({len(filtered_data)} Titik Terdeteksi)")

# Menampilkan peta interaktif berdasarkan kolom lat dan lon dari data yang sudah difilter
st.map(filtered_data[["lat", "lon"]])

# Membuat checkbox interaktif untuk menampilkan tabel data mentah
if st.checkbox("Tampilkan Tabel Data Mentah"):
    st.dataframe(
        filtered_data[["name", "year", "mass_kg", "class", "fall", "lat", "lon"]]
    )