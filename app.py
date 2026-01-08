import math
import streamlit as st

# -----------------------------
# Queueing M/M/2 (Erlang-C)
# -----------------------------
def mmc_erlang_c(interarrival_min: float, service_min: float, c: int = 2):
    """
    Menghitung metrik antrian M/M/c dengan rumus Erlang-C.
    Semua satuan waktu dalam MENIT.
    """
    lam = 1.0 / interarrival_min       # λ (customers per minute)
    mu = 1.0 / service_min             # μ (customers per minute per server)
    rho = lam / (c * mu)               # utilization

    if rho >= 1.0:
        raise ValueError("Sistem tidak stabil karena ρ ≥ 1. Kurangi kedatangan atau percepat pelayanan.")

    a = lam / mu  # offered load

    # P0
    sum_terms = sum((a ** n) / math.factorial(n) for n in range(c))
    last_term = (a ** c) / math.factorial(c) * (1.0 / (1.0 - rho))
    P0 = 1.0 / (sum_terms + last_term)

    # Erlang-C: probability an arrival must wait (Pw)
    Pw = last_term * P0

    # Lq, Wq, W
    Lq = P0 * ((a ** c) * rho) / (math.factorial(c) * ((1.0 - rho) ** 2))
    Wq = Lq / lam
    W = Wq + (1.0 / mu)

    return {
        "lambda": lam,
        "mu": mu,
        "c": c,
        "rho": rho,
        "a": a,
        "P0": P0,
        "Pw": Pw,
        "Lq": Lq,
        "Wq": Wq,
        "W": W,
        "L": lam * W,
    }


# -----------------------------
# UI Streamlit
# -----------------------------
st.set_page_config(page_title="Queueing Theory Calculator - M/M/2", page_icon="🧮", layout="centered")

st.title("🧮 Queueing Theory Calculator")
st.caption("Model: **M/M/2** (dua pelayan) — rumus standar **Erlang-C**. Semua input dalam **menit**.")

with st.container(border=True):
    st.subheader("Input")
    col1, col2 = st.columns(2)
    with col1:
        interarrival = st.number_input(
            "Waktu antar kedatangan (menit)",
            min_value=0.0001,
            value=4.0,
            step=0.5,
            help="Contoh soal: 4 menit/pelanggan"
        )
    with col2:
        service_time = st.number_input(
            "Waktu pelayanan per pelayan (menit)",
            min_value=0.0001,
            value=3.0,
            step=0.5,
            help="Contoh soal: 3 menit/pelanggan"
        )

    c = st.selectbox("Jumlah pelayan (server)", options=[2], index=0, help="Sesuai soal: 2 loket")

    hitung = st.button("Calculate", type="primary", use_container_width=True)


if hitung:
    try:
        # Validasi
        if interarrival <= 0 or service_time <= 0:
            st.error("Input harus bernilai positif (> 0).")
            st.stop()

        res = mmc_erlang_c(interarrival, service_time, c=c)

        st.success("Perhitungan berhasil ✅")

        # =========================================================
        # GABUNG: Proses Pengerjaan + Hasil dalam SATU KOTAK (border)
        # =========================================================
        with st.container(border=True):

            # -----------------------------
            # Tampilkan proses pengerjaan (step-by-step)
            # -----------------------------
            st.subheader("Proses Pengerjaan (Step-by-step)")

            lam = res["lambda"]
            mu = res["mu"]
            rho = res["rho"]
            a = res["a"]
            P0 = res["P0"]
            Lq = res["Lq"]
            Wq = res["Wq"]
            W = res["W"]

            st.markdown("### 1) Hitung λ dan μ")
            st.latex(r"\lambda = \frac{1}{\text{waktu antar kedatangan}}")
            st.latex(rf"\lambda = \frac{{1}}{{{interarrival:.6g}}} = {lam:.6f}\ \text{{pelanggan/menit}}")
            st.latex(r"\mu = \frac{1}{\text{waktu pelayanan per pelayan}}")
            st.latex(rf"\mu = \frac{{1}}{{{service_time:.6g}}} = {mu:.6f}\ \text{{pelanggan/menit}}")

            st.markdown("### 2) Utilisasi (ρ)")
            st.latex(r"\rho = \frac{\lambda}{c\mu}")
            st.latex(rf"\rho = \frac{{{lam:.6f}}}{{{c}\times {mu:.6f}}} = {rho:.6f}")
            st.write(f"Utilisasi tiap pelayan ≈ **{rho*100:.2f}%**")

            st.markdown("### 3) Komponen Erlang-C untuk M/M/2")
            st.latex(r"a = \frac{\lambda}{\mu}")
            st.latex(rf"a = \frac{{{lam:.6f}}}{{{mu:.6f}}} = {a:.6f}")

            # ====== P0: rumus + substitusi singkat ======
            st.latex(
                r"P_0 = \left[\sum_{n=0}^{c-1}\frac{a^n}{n!} + \frac{a^c}{c!}\cdot\frac{1}{1-\rho}\right]^{-1}"
            )
            st.latex(
                rf"P_0 = \left[1 + {a:.6f} + \frac{{{a:.6f}^2}}{{2!}}\cdot\frac{{1}}{{1-{rho:.6f}}}\right]^{-1}"
            )
            st.latex(rf"P_0 = {P0:.6f}")

            # ====== Lq: rumus + substitusi singkat ======
            st.latex(r"L_q = P_0\cdot\frac{a^c\cdot\rho}{c!\,(1-\rho)^2}")
            st.latex(
                rf"L_q = {P0:.6f}\cdot\frac{{{a:.6f}^2\cdot {rho:.6f}}}{{2!\cdot(1-{rho:.6f})^2}}"
            )
            st.latex(rf"L_q = {Lq:.6f}")

            # ====== Wq: pisah jadi 3 baris (sesuai format yang Anda mau) ======
            st.latex(r"W_q = \frac{L_q}{\lambda}")
            st.latex(rf"W_q = \frac{{{Lq:.6f}}}{{{lam:.6f}}}")
            st.latex(rf"W_q = {Wq:.6f}\ \text{{menit}}")

            # ====== W: pisah jadi 3 baris (sesuai format yang Anda mau) ======
            st.latex(r"W = W_q + \frac{1}{\mu}")
            st.latex(rf"W = {Wq:.6f} + \frac{{1}}{{{mu:.6f}}}")
            st.latex(rf"W = {W:.6f}\ \text{{menit}}")

            st.divider()

            # -----------------------------
            # Ringkasan hasil (mirip contoh app)
            # -----------------------------
            st.subheader("Hasil (M/M/2 results)")
            colA, colB = st.columns(2)

            with colA:
                st.metric("λ (arrival rate)", f"{lam:.6f} / menit")
                st.metric("μ (service rate)", f"{mu:.6f} / menit")
                st.metric("ρ (utilization)", f"{rho:.6f}  ({rho*100:.2f}%)")

            with colB:
                st.metric("W (time in system)", f"{W:.6f} menit")
                st.metric("Wq (time in queue)", f"{Wq:.6f} menit")
                st.metric("Lq (avg queue length)", f"{Lq:.6f}")

        st.info(
            "Catatan: Jika Anda mengerjakan **Bagian 1 manual** dengan rumus Erlang-C yang sama, "
            "maka hasil manual dan hasil aplikasi akan **identik**."
        )

    except Exception as e:
        st.error(f"Terjadi error: {e}")
