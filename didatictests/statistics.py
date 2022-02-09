# import matplotlib.lines as lines
from matplotlib import lines  # noqa: F401
from matplotlib import pyplot as plt  # noqa: F401
import numpy as np  # noqa: F401
from scipy.stats import norm  # noqa: F401
from scipy.stats import t as student  # noqa: F401
from matplotlib.gridspec import GridSpec  # noqa: F401


def pop_mean_test(
    mu=None,
    sigma=None,
    x_bar=None,
    n=1,
    span=5,
    conf=0.95,
    alt_hip="different",
    calc_p=True,
    dist="norm",
    n_student=None,
    title="Teste de média populacional",
):
    ppf = norm.ppf
    pdf = norm.pdf
    cdf = norm.cdf
    sf = norm.sf

    if dist == "student":

        def partial(fn, df):
            def new_fn(q):
                return fn(q, df=df)

            return new_fn

        if n_student is None:
            n_student = n
        df = n_student - 1
        ppf = partial(student.ppf, df)
        pdf = partial(student.pdf, df)
        cdf = partial(student.cdf, df)
        sf = partial(student.sf, df)

    mean_sigma = sigma / np.sqrt(n)
    signif = 1 - conf

    # Funções de conversão entre a normal padrão e a normal dos dados
    def standardize(x):
        z = (x - mu) / (mean_sigma)
        return z

    def destandardize(z):
        x = z * mean_sigma + mu
        return x

    # Cálculo dos parâmetros normalizados
    z = standardize(x_bar)
    z_alpha_inf = ppf(signif / 2) if alt_hip == "different" else ppf(signif)
    z_alpha_sup = ppf(1 - signif / 2) if alt_hip == "different" else ppf(1 - signif)
    z_range = [-span - 0.5, span + 0.5]

    # Cálculo dos parâmetros não normalizados
    x_bar_alpha_inf = destandardize(z_alpha_inf)
    x_bar_alpha_sup = destandardize(z_alpha_sup)
    x_range = [destandardize(z_range[0]), destandardize(z_range[1])]

    # Plot stuff
    plt.style.use("default")
    fig = plt.figure(figsize=(15, 5), dpi=300)
    fig.suptitle(title, y=0.92, va="center", size=22)
    # fig.suptitle(title)
    gs = GridSpec(1, 2, width_ratios=[8, 3])
    graph = fig.add_subplot(gs[0])

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    line_color = colors[0]
    conf_color = colors[1]
    signif_color = colors[2]
    p_color = "black"

    # Plotar a curva normal
    x = np.linspace(-span, span, 1024)
    y = pdf(x)
    y_max = y.max() * 1.1
    y_x_sec = -y_max * 0.25
    graph.plot(x, y, linewidth=1.5, linestyle="-", color=line_color)

    # Ajeitar a linha dos eixos
    graph.spines["right"].set_color("none")
    graph.spines["left"].set_color("none")
    graph.spines["top"].set_color("none")
    graph.yaxis.set_visible(False)
    # Eixo X primário:
    graph.xaxis.set_ticks_position("bottom")
    graph.spines["bottom"].set_position(("data", 0))
    graph.set_xlim(z_range[0], z_range[1])
    x_ticks = np.linspace(-span, span, 1 + 2 * span)
    graph.set_xticks(x_ticks)
    graph.set_xlabel("$N(0;1)$")
    graph.xaxis.set_label_coords(0, 0.29)

    # Eixo X secundário
    # Adicionar espaço inferior
    fig.subplots_adjust(bottom=0.2)

    def tick_function(X):
        return [f"{x:.1f}" for x in X]

    # Copiar e configurar exibições
    graph_x_sec = graph.twiny()
    graph_x_sec.xaxis.set_ticks_position("bottom")
    graph_x_sec.xaxis.set_label_position("bottom")
    # graph_x_sec.spines["top"].set_position(("data", y_max))
    # graph_x_sec.set_frame_on(True)
    graph_x_sec.patch.set_visible(False)
    for sp in graph_x_sec.spines.values():
        sp.set_visible(False)
    graph_x_sec.spines["bottom"].set_visible(True)
    graph_x_sec.spines["bottom"].set_position(("data", y_x_sec))
    x_sec_ticks = destandardize(x_ticks)
    graph_x_sec.set_xticks(x_sec_ticks)
    graph_x_sec.set_xticklabels(tick_function(x_sec_ticks))
    graph_x_sec.set_xlim(x_range[0], x_range[1])
    graph_x_sec.set_xlabel(
        "$"
        + f"N({mu:.2f}".rstrip("0").rstrip(".")
        + f";{sigma:.2f}".rstrip("0").rstrip(".")
        + ")$"
    )
    graph_x_sec.xaxis.set_label_coords(0, 0.10)

    is_within_span = -span < z and z < span
    if not (x_bar is None):
        if is_within_span:
            # Ponto Z no eixo x, na curva e linha pontilhada
            graph.plot(
                [z, z],
                [0, pdf(z)],
                color="black",
                linewidth=1,
                linestyle="--",
                alpha=0.75,
                zorder=1,
            )
            graph.scatter(
                [
                    z,
                ],
                [
                    pdf(z),
                ],
                30,
                color=line_color,
                alpha=1,
                zorder=10,
            )
            graph.scatter(
                [
                    z,
                ],
                [
                    0,
                ],
                30,
                color="black",
                alpha=1,
                zorder=10,
            )
            # Anotação do ponto Z
            z_not = f"$Z={z:.3f}$"
            t_not = "$t_{" + f"{n-1}" + "}" + f"={z:.3f}$"
            graph.annotate(
                z_not if dist == "norm" else t_not,
                xy=(z, 0),
                xycoords="data",
                # xytext=(-30, -30), textcoords='offset points', fontsize=16,
                xytext=(0.5, 0.14),
                textcoords="axes fraction",
                fontsize=16,
                va="center",
                ha="center",
                arrowprops=dict(
                    arrowstyle="->",
                    alpha=0.7,
                    connectionstyle="arc3,rad=.2" if z > 0 else "arc3,rad=-.2",
                ),
                zorder=10,
            )

            graph_x_sec.plot(
                [x_bar, x_bar],
                [y_x_sec, 0],
                color="black",
                linewidth=1,
                linestyle="--",
                alpha=0.75,
                zorder=1,
            )
            graph_x_sec.scatter(
                [
                    x_bar,
                ],
                [
                    y_x_sec,
                ],
                30,
                color="black",
                alpha=1,
                zorder=10,
            )
            # Anotação do ponto x_bar
            graph.annotate(
                r"$\overline{x}$" + f"={x_bar}",
                xy=(z, y_x_sec),
                xycoords="data",
                # xytext=(-30, -30), textcoords='offset points', fontsize=16,
                xytext=(0.5, -0.07),
                textcoords="axes fraction",
                fontsize=16,
                va="center",
                ha="center",
                arrowprops=dict(
                    arrowstyle="->",
                    alpha=0.7,
                    connectionstyle="arc3,rad=.2" if z > 0 else "arc3,rad=-.2",
                ),
                zorder=10,
            )

        # Se o z estiver fora do alcance do gráfico
        else:
            # Anotação do ponto Z
            z_not = f"$Z={z:.3f}$"
            t_not = "$t_{" + f"{n-1}" + "}" + f"={z:.3f}$"
            pos_x = (span + 0.5) if z > 0 else -(span + 0.5)
            graph.annotate(
                z_not if dist == "norm" else t_not,
                xy=(pos_x, -y_max * 0.05),
                xycoords="data",
                # xytext=(-30, -30), textcoords='offset points', fontsize=16,
                xytext=(0.5, 0.14),
                textcoords="axes fraction",
                fontsize=16,
                va="center",
                ha="center",
                arrowprops=dict(
                    arrowstyle="->",
                    ls="dashed",
                    alpha=0.7,
                    connectionstyle="angle,angleA=0, angleB=30, rad=30"
                    if z > 0
                    else "angle,angleA=0, angleB=-30, rad=30",
                ),
                zorder=10,
            )
            # Anotação do ponto x_bar
            graph.annotate(
                r"$\overline{x}$" + f"={x_bar}",
                xy=(pos_x, y_x_sec - y_max * 0.05),
                xycoords="data",
                # xytext=(-30, -30), textcoords='offset points', fontsize=16,
                xytext=(0.5, -0.07),
                textcoords="axes fraction",
                fontsize=16,
                va="center",
                ha="center",
                arrowprops=dict(
                    arrowstyle="->",
                    ls="dashed",
                    alpha=0.7,
                    connectionstyle="angle,angleA=0, angleB=30, rad=30"
                    if z > 0
                    else "angle,angleA=0, angleB=-30, rad=30",
                ),
                zorder=10,
            )

        if calc_p:
            if alt_hip == "less":
                p = cdf(z)
                if is_within_span:
                    filled_x_p = x[x < z]
                    filled_y_p = pdf(filled_x_p)
                    graph.fill_between(
                        filled_x_p,
                        filled_y_p,
                        facecolor="none",
                        alpha=0.5,
                        hatch="////",
                        edgecolor=p_color,
                        label=f"p = {p:.3f}",
                    )

            elif alt_hip == "greater":
                p = sf(z)
                if is_within_span:
                    filled_x_p = x[x > z]
                    filled_y_p = pdf(filled_x_p)
                    graph.fill_between(
                        filled_x_p,
                        filled_y_p,
                        facecolor="none",
                        alpha=0.5,
                        hatch="////",
                        edgecolor=p_color,
                        label=f"p = {p:.3f}",
                    )

            elif alt_hip == "different":
                if z > 0:
                    p = sf(z) * 2
                else:
                    p = cdf(z) * 2
                if is_within_span:
                    z_p_sup = z if z > 0 else -z
                    z_p_inf = z if z < 0 else -z
                    filled_x_p = x[x < z_p_inf]
                    filled_y_p = pdf(filled_x_p)
                    graph.fill_between(
                        filled_x_p,
                        filled_y_p,
                        facecolor="none",
                        alpha=0.5,
                        hatch="////",
                        edgecolor=p_color,
                        label=f"p = {p:.3f}",
                    )
                    filled_x_p = x[x > z_p_sup]
                    filled_y_p = pdf(filled_x_p)
                    graph.fill_between(
                        filled_x_p,
                        filled_y_p,
                        facecolor="none",
                        alpha=0.5,
                        hatch="////",
                        edgecolor=p_color,
                    )

    if not (conf is None):
        if alt_hip == "different" or alt_hip == "less":
            if alt_hip == "less":
                z_alpha_sup = span
            graph.scatter(
                [
                    z_alpha_inf,
                ],
                [
                    0,
                ],
                20,
                color=conf_color,
                alpha=1,
                zorder=10,
            )
            # Anotação do ponto z_alpha_inf
            z_not = r"$-Z_{\alpha/2}$" if alt_hip == "different" else r"$-Z_{\alpha}$"
            t_not = r"$-t_{\alpha/2}$" if alt_hip == "different" else r"$-t_{\alpha}$"
            notacao_z_inf = z_not if dist == "norm" else t_not
            graph.annotate(
                f"{notacao_z_inf}$={z_alpha_inf:.03f}$",
                xy=(z_alpha_inf, 0),
                xycoords="data",
                # xytext=(-70, 50), textcoords='offset points', fontsize=16,
                xytext=(0.03, 0.30),
                textcoords="axes fraction",
                fontsize=16,
                va="bottom",
                arrowprops=dict(
                    arrowstyle="->",
                    alpha=0.7,
                    connectionstyle="arc3,rad=-.2",
                    color=conf_color,
                ),
            )

            graph_x_sec.scatter(
                [
                    x_bar_alpha_inf,
                ],
                [
                    y_x_sec,
                ],
                20,
                color=conf_color,
                alpha=1,
                zorder=10,
            )
            graph_x_sec.plot(
                [x_bar_alpha_inf, x_bar_alpha_inf],
                [y_x_sec, 0],
                color=conf_color,
                linewidth=1,
                linestyle="--",
                alpha=0.75,
                zorder=1,
            )
            # Anotação do ponto x_bar_alpha_inf
            notacao_x_inf = (
                r"$\overline{x}_{\alpha_{inf}}$"
                if alt_hip == "different"
                else r"$\overline{x}_{\alpha}$"
            )
            graph.annotate(
                f"{notacao_x_inf}$={x_bar_alpha_inf:.03f}$",
                xy=(z_alpha_inf, y_x_sec),
                xycoords="data",
                # xytext=(-70, 50), textcoords='offset points', fontsize=16,
                xytext=(0.03, -0.05),
                textcoords="axes fraction",
                fontsize=16,
                va="top",
                arrowprops=dict(
                    arrowstyle="->",
                    alpha=0.7,
                    connectionstyle="arc3,rad=.2",
                    color=conf_color,
                ),
            )

        if alt_hip == "different" or alt_hip == "greater":
            if alt_hip == "greater":
                z_alpha_inf = -span
            graph.scatter(
                [
                    z_alpha_sup,
                ],
                [
                    0,
                ],
                20,
                color=conf_color,
                alpha=1,
                zorder=10,
            )
            # Anotação do ponto z_alpha_sup
            z_not = r"$Z_{\alpha/2}$" if alt_hip == "different" else r"$Z_{\alpha}$"
            t_not = r"$t_{\alpha/2}$" if alt_hip == "different" else r"$t_{\alpha}$"
            notacao_z_sup = z_not if dist == "norm" else t_not
            graph.annotate(
                f"{notacao_z_sup}={z_alpha_sup:.03f}",
                xy=(z_alpha_sup, 0),
                xycoords="data",
                # xytext=(20, 50), textcoords='offset points', fontsize=16,
                xytext=(0.97, 0.30),
                textcoords="axes fraction",
                fontsize=16,
                va="bottom",
                ha="right",
                arrowprops=dict(
                    arrowstyle="->",
                    alpha=0.7,
                    connectionstyle="arc3,rad=.2",
                    color=conf_color,
                ),
            )

            graph_x_sec.scatter(
                [
                    x_bar_alpha_sup,
                ],
                [
                    y_x_sec,
                ],
                20,
                color=conf_color,
                alpha=1,
                zorder=10,
            )
            graph_x_sec.plot(
                [x_bar_alpha_sup, x_bar_alpha_sup],
                [y_x_sec, 0],
                color=conf_color,
                linewidth=1,
                linestyle="--",
                alpha=0.75,
                zorder=1,
            )
            # Anotação do ponto x_bar_alpha_sup
            notacao_x_sup = (
                r"$\overline{x}_{\alpha_{sup}}$"
                if alt_hip == "different"
                else r"$\overline{x}_{\alpha}$"
            )
            graph.annotate(
                f"{notacao_x_sup}$={x_bar_alpha_sup:.03f}$",
                xy=(z_alpha_sup, y_x_sec),
                xycoords="data",
                # xytext=(-70, 50), textcoords='offset points', fontsize=16,
                xytext=(0.97, -0.05),
                textcoords="axes fraction",
                fontsize=16,
                va="top",
                ha="right",
                arrowprops=dict(
                    arrowstyle="->",
                    alpha=0.7,
                    connectionstyle="arc3,rad=-.2",
                    color=conf_color,
                ),
            )

        # Área de confiança
        filled_x = x[(x > z_alpha_inf) & (x < z_alpha_sup)]
        filled_y = pdf(filled_x)
        graph.fill_between(
            filled_x,
            filled_y,
            color=conf_color,
            alpha=0.25,
            label=f"Confiança = {conf:.3f}",
        )

        # Área de significância
        filled_x_1 = x[x < z_alpha_inf]
        filled_x_2 = x[x > z_alpha_sup]
        filled_y_1 = pdf(filled_x_1)
        filled_y_2 = pdf(filled_x_2)
        graph.fill_between(
            filled_x_1,
            filled_y_1,
            color=signif_color,
            alpha=0.25,
            label=f"Significância = {signif:.3f}",
        )
        graph.fill_between(filled_x_2, filled_y_2, color=signif_color, alpha=0.25)

    graph.legend(loc="upper left")

    resolucao = fig.add_subplot(gs[1])
    resolucao.spines["right"].set_color("none")
    resolucao.spines["top"].set_color("none")
    resolucao.spines["bottom"].set_color("none")
    resolucao.spines["left"].set_color("none")
    resolucao.xaxis.set_visible(False)
    resolucao.yaxis.set_visible(False)

    texto = ""
    texto += r"$\mu_0 = $" + f"{mu:.3f}\n"
    texto += r"$\overline{x}$" + f"={x_bar:.3f}\n"
    texto += (
        r"$\sigma = " + f"{sigma:.3f}$\n"
        if dist == "norm"
        else "$S_x = " + f"{sigma:.3f}$\n"
    )
    texto += f"$n={n}$\n"
    z_formula = r"$Z = \frac{\overline{x}-\mu_0}{\sigma/\sqrt{n}} =" + f"{z:.3f}$\n"
    t_formula = r"$t_{n-1} = \frac{\overline{x}-\mu_0}{S_x/\sqrt{n}} =" + f"{z:.3f}$\n"
    texto += z_formula if dist == "norm" else t_formula
    texto += r"$Confiança = " + f"{conf:.3f}$ (área laranja)\n"
    texto += r"$Significancia = " + f"{1-conf:.3f}$ (área verde)\n\n"

    if alt_hip == "different":
        texto += r"$H_0: \mu=\mu_0$" + "\n"
        texto += r"$H_1: \mu\neq\mu_0$" + "\n\n\n"

        texto += "Limites do intervalo de confiança:" + "\n"
        texto += "\t" + f"• {notacao_z_inf}$={z_alpha_inf:.3f}$" + "\n"
        texto += "\t" + f"• {notacao_z_sup}$={z_alpha_sup:.3f}$" + "\n"
        texto += "\t" + r"• $p = $" + f"{p:.7f} (área hachurada)" + "\n\n\n"

        z_or_t_mod = "$|Z|$" if dist == "norm" else "$|t|$"
        # rejeito H0
        if p < 1 - conf:
            # texto += z_or_t + r"\notin$" + f"[{notacao_z_inf},{notacao_z_sup}]" + "\n"
            texto += z_or_t_mod + f"$>${notacao_z_sup}" + "\n"
            texto += r"$\therefore\;rejeito\;H_0$" + "\n\n"
            texto += r"$p < Significancia$" + "\n"
            texto += r"$\therefore\;rejeito\;H_0$" + "\n"
        # aceito H0
        else:
            # texto += z_or_t + r"\in$" + f"[{notacao_z_inf},{notacao_z_sup}]" + "\n"
            texto += z_or_t_mod + f"$\leq${notacao_z_sup}" + "\n"  # noqa: W605
            texto += r"$\therefore\;aceito\;H_0$" + "\n\n"
            texto += r"$p \geq Significancia$" + "\n"
            texto += r"$\therefore\;aceito\;H_0$" + "\n"

    elif alt_hip == "greater":
        texto += r"$H_0: \mu\leq\mu_0$" + "\n"
        texto += r"$H_1: \mu>\mu_0$" + "\n\n\n"

        texto += "Valores críticos:" + "\n"
        texto += "\t" + f"• {notacao_z_sup}$={z_alpha_sup:.3f}$" + "\n"
        texto += "\t" + r"• $p = " + f"{p:.7f}$ (área hachurada)" + "\n\n\n"

        # rejeito H0
        if p < signif:
            z_or_t = "$Z > $" if dist == "norm" else "$t > $"
            texto += z_or_t + notacao_z_sup + "\n"
            texto += r"$\therefore\;rejeito\;H_0$" + "\n\n"
            texto += r"$p < Significancia$" + "\n"
            texto += r"$\therefore\;rejeito\;H_0$" + "\n"
        # aceito H0
        else:
            z_or_t = "$Z < $" if dist == "norm" else "$t < $"
            texto += z_or_t + notacao_z_sup + "\n"
            texto += r"$\therefore\;aceito\;H_0$" + "\n\n"
            texto += r"$p \geq Significancia$" + "\n"
            texto += r"$\therefore\;aceito\;H_0$" + "\n"

    elif alt_hip == "less":
        texto += r"$H_0: \mu\geq\mu_0$" + "\n"
        texto += r"$H_1: \mu<\mu_0$" + "\n\n\n"

        texto += "Valores críticos:" + "\n"
        texto += "\t" + f"• {notacao_z_inf}$={z_alpha_inf:.3f}$" + "\n"
        texto += "\t" + r"• $p = " + f"{p:.7f}$ (área hachurada)" + "\n\n\n"

        # rejeito H0
        if p < signif:
            z_or_t = "$Z < $" if dist == "norm" else "$t < $"
            texto += z_or_t + notacao_z_inf + "\n"
            texto += r"$\therefore\;rejeito\;H_0$" + "\n\n"
            texto += r"$p < Significancia$" + "\n"
            texto += r"$\therefore\;rejeito\;H_0$" + "\n"
        # aceito H0
        else:
            z_or_t = "$Z > $" if dist == "norm" else "$t > $"
            texto += z_or_t + notacao_z_inf + "\n"
            texto += r"$\therefore\;aceito\;H_0$" + "\n\n"
            texto += r"$p \geq Significancia$" + "\n"
            texto += r"$\therefore\;aceito\;H_0$" + "\n"

    resolucao.text(0, 1, texto, ha="left", va="top")


def pop_mean_interval(
    sigma=None,
    x_bar=None,
    n=1,
    span=5,
    conf=0.95,
    alt_hip="different",
    calc_p=True,
    dist="norm",
    n_student=None,
    title="Intervalo de confiança para a média",
):
    mu = x_bar
    ppf = norm.ppf
    pdf = norm.pdf
    # cdf = norm.cdf
    # sf = norm.sf

    if dist == "student":

        def partial(fn, df):
            def new_fn(q):
                return fn(q, df=df)

            return new_fn

        if n_student is None:
            n_student = n
        df = n_student - 1
        ppf = partial(student.ppf, df)
        pdf = partial(student.pdf, df)
        # cdf = partial(student.cdf, df)
        # sf = partial(student.sf, df)

    mean_sigma = sigma / np.sqrt(n)
    signif = 1 - conf

    # Funções de conversão entre a normal padrão e a normal dos dados
    def standardize(x):
        z = (x - mu) / (mean_sigma)
        return z

    def destandardize(z):
        x = z * mean_sigma + mu
        return x

    # Cálculo dos parâmetros normalizados
    # z = standardize(x_bar)
    z_alpha_inf = ppf(signif / 2) if alt_hip == "different" else ppf(signif)
    z_alpha_sup = ppf(1 - signif / 2) if alt_hip == "different" else ppf(1 - signif)
    z_range = [-span - 0.5, span + 0.5]

    # Cálculo dos parâmetros não normalizados
    x_bar_alpha_inf = destandardize(z_alpha_inf)
    x_bar_alpha_sup = destandardize(z_alpha_sup)
    x_range = [destandardize(z_range[0]), destandardize(z_range[1])]

    # Plot stuff
    plt.style.use("default")
    fig = plt.figure(figsize=(15, 5), dpi=300)
    fig.suptitle(title, y=0.92, va="center", size=22)
    # fig.suptitle(title)
    gs = GridSpec(1, 2, width_ratios=[8, 3])
    graph = fig.add_subplot(gs[0])

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    line_color = colors[0]
    conf_color = colors[1]
    signif_color = colors[2]

    # Plotar a curva normal
    x = np.linspace(-span, span, 1024)
    y = pdf(x)
    y_max = y.max() * 1.1
    y_x_sec = -y_max * 0.25
    graph.plot(x, y, linewidth=1.5, linestyle="-", color=line_color)

    # Ajeitar a linha dos eixos
    graph.spines["right"].set_color("none")
    graph.spines["left"].set_color("none")
    graph.spines["top"].set_color("none")
    graph.yaxis.set_visible(False)
    # Eixo X primário:
    graph.xaxis.set_ticks_position("bottom")
    graph.spines["bottom"].set_position(("data", 0))
    graph.set_xlim(z_range[0], z_range[1])
    x_ticks = np.linspace(-span, span, 1 + 2 * span)
    graph.set_xticks(x_ticks)
    graph.set_xlabel("$N(0;1)$")
    graph.xaxis.set_label_coords(0, 0.29)

    # Eixo X secundário
    # Adicionar espaço inferior
    fig.subplots_adjust(bottom=0.2)

    def tick_function(X):
        return [f"{x:.1f}" for x in X]

    # Copiar e configurar exibições
    graph_x_sec = graph.twiny()
    graph_x_sec.xaxis.set_ticks_position("bottom")
    graph_x_sec.xaxis.set_label_position("bottom")
    # graph_x_sec.spines["top"].set_position(("data", y_max))
    # graph_x_sec.set_frame_on(True)
    graph_x_sec.patch.set_visible(False)
    for sp in graph_x_sec.spines.values():
        sp.set_visible(False)
    graph_x_sec.spines["bottom"].set_visible(True)
    graph_x_sec.spines["bottom"].set_position(("data", y_x_sec))
    x_sec_ticks = destandardize(x_ticks)
    graph_x_sec.set_xticks(x_sec_ticks)
    graph_x_sec.set_xticklabels(tick_function(x_sec_ticks))
    graph_x_sec.set_xlim(x_range[0], x_range[1])
    graph_x_sec.set_xlabel(
        "$"
        + f"N({mu:.2f}".rstrip("0").rstrip(".")
        + f";{sigma:.2f}".rstrip("0").rstrip(".")
        + ")$"
    )
    graph_x_sec.xaxis.set_label_coords(0, 0.10)

    if not (conf is None):
        if alt_hip == "different" or alt_hip == "less":
            if alt_hip == "less":
                z_alpha_sup = span
            graph.scatter(
                [
                    z_alpha_inf,
                ],
                [
                    0,
                ],
                20,
                color=conf_color,
                alpha=1,
                zorder=10,
            )
            # Anotação do ponto z_alpha_inf
            z_not = r"$-Z_{\alpha/2}$" if alt_hip == "different" else r"$-Z_{\alpha}$"
            t_not = r"$-t_{\alpha/2}$" if alt_hip == "different" else r"$-t_{\alpha}$"
            notacao_z_inf = z_not if dist == "norm" else t_not
            graph.annotate(
                f"{notacao_z_inf}$={z_alpha_inf:.03f}$",
                xy=(z_alpha_inf, 0),
                xycoords="data",
                # xytext=(-70, 50), textcoords='offset points', fontsize=16,
                xytext=(0.03, 0.30),
                textcoords="axes fraction",
                fontsize=16,
                va="bottom",
                arrowprops=dict(
                    arrowstyle="->",
                    alpha=0.7,
                    connectionstyle="arc3,rad=-.2",
                    color=conf_color,
                ),
            )

            graph_x_sec.scatter(
                [
                    x_bar_alpha_inf,
                ],
                [
                    y_x_sec,
                ],
                20,
                color=conf_color,
                alpha=1,
                zorder=10,
            )
            graph_x_sec.plot(
                [x_bar_alpha_inf, x_bar_alpha_inf],
                [y_x_sec, 0],
                color=conf_color,
                linewidth=1,
                linestyle="--",
                alpha=0.75,
                zorder=1,
            )
            # Anotação do ponto x_bar_alpha_inf
            notacao_x_inf = (
                r"$\overline{x}_{\alpha_{inf}}$"
                if alt_hip == "different"
                else r"$\overline{x}_{\alpha}$"
            )
            graph.annotate(
                f"{notacao_x_inf}$={x_bar_alpha_inf:.03f}$",
                xy=(z_alpha_inf, y_x_sec),
                xycoords="data",
                # xytext=(-70, 50), textcoords='offset points', fontsize=16,
                xytext=(0.03, -0.05),
                textcoords="axes fraction",
                fontsize=16,
                va="top",
                arrowprops=dict(
                    arrowstyle="->",
                    alpha=0.7,
                    connectionstyle="arc3,rad=.2",
                    color=conf_color,
                ),
            )

        if alt_hip == "different" or alt_hip == "greater":
            if alt_hip == "greater":
                z_alpha_inf = -span
            graph.scatter(
                [
                    z_alpha_sup,
                ],
                [
                    0,
                ],
                20,
                color=conf_color,
                alpha=1,
                zorder=10,
            )
            # Anotação do ponto z_alpha_sup
            z_not = r"$Z_{\alpha/2}$" if alt_hip == "different" else r"$Z_{\alpha}$"
            t_not = r"$t_{\alpha/2}$" if alt_hip == "different" else r"$t_{\alpha}$"
            notacao_z_sup = z_not if dist == "norm" else t_not
            graph.annotate(
                f"{notacao_z_sup}={z_alpha_sup:.03f}",
                xy=(z_alpha_sup, 0),
                xycoords="data",
                # xytext=(20, 50), textcoords='offset points', fontsize=16,
                xytext=(0.97, 0.30),
                textcoords="axes fraction",
                fontsize=16,
                va="bottom",
                ha="right",
                arrowprops=dict(
                    arrowstyle="->",
                    alpha=0.7,
                    connectionstyle="arc3,rad=.2",
                    color=conf_color,
                ),
            )

            graph_x_sec.scatter(
                [
                    x_bar_alpha_sup,
                ],
                [
                    y_x_sec,
                ],
                20,
                color=conf_color,
                alpha=1,
                zorder=10,
            )
            graph_x_sec.plot(
                [x_bar_alpha_sup, x_bar_alpha_sup],
                [y_x_sec, 0],
                color=conf_color,
                linewidth=1,
                linestyle="--",
                alpha=0.75,
                zorder=1,
            )
            # Anotação do ponto x_bar_alpha_sup
            notacao_x_sup = (
                r"$\overline{x}_{\alpha_{sup}}$"
                if alt_hip == "different"
                else r"$\overline{x}_{\alpha}$"
            )
            graph.annotate(
                f"{notacao_x_sup}$={x_bar_alpha_sup:.03f}$",
                xy=(z_alpha_sup, y_x_sec),
                xycoords="data",
                # xytext=(-70, 50), textcoords='offset points', fontsize=16,
                xytext=(0.97, -0.05),
                textcoords="axes fraction",
                fontsize=16,
                va="top",
                ha="right",
                arrowprops=dict(
                    arrowstyle="->",
                    alpha=0.7,
                    connectionstyle="arc3,rad=-.2",
                    color=conf_color,
                ),
            )

        # Área de confiança
        filled_x = x[(x > z_alpha_inf) & (x < z_alpha_sup)]
        filled_y = pdf(filled_x)
        graph.fill_between(
            filled_x,
            filled_y,
            color=conf_color,
            alpha=0.25,
            label=f"Confiança = {conf:.3f}",
        )

        # Área de significância
        filled_x_1 = x[x < z_alpha_inf]
        filled_x_2 = x[x > z_alpha_sup]
        filled_y_1 = pdf(filled_x_1)
        filled_y_2 = pdf(filled_x_2)
        graph.fill_between(
            filled_x_1,
            filled_y_1,
            color=signif_color,
            alpha=0.25,
            label=f"Significância = {signif:.3f}",
        )
        graph.fill_between(filled_x_2, filled_y_2, color=signif_color, alpha=0.25)

    graph.legend(loc="upper left")

    resolucao = fig.add_subplot(gs[1])
    resolucao.spines["right"].set_color("none")
    resolucao.spines["top"].set_color("none")
    resolucao.spines["bottom"].set_color("none")
    resolucao.spines["left"].set_color("none")
    resolucao.xaxis.set_visible(False)
    resolucao.yaxis.set_visible(False)

    texto = ""
    texto += f"$n={n}$\n"
    texto += r"$\mu_0 = \overline{x}" + f"={x_bar:.3f}$\n"
    texto += (
        r"$\sigma = " + f"{sigma}$\n"
        if dist == "norm"
        else "$S_x = " + f"{sigma:.3f}$\n"
    )
    texto += (
        r"$\sigma_{\overline{x}} = \sigma/\sqrt{n} = " + f"{sigma/np.sqrt(n):.3f}$\n"
    )
    texto += r"$Confiança = " + f"{conf:.3f}$ (área laranja)\n"
    texto += r"$Significancia = " + f"{1-conf:.3f}$ (área verde)\n\n"

    if alt_hip == "different":
        texto += "Limites do intervalo de confiança:" + "\n"
        texto += "\t" + f"• {notacao_z_inf}$={z_alpha_inf:.3f}$" + "\n"
        texto += "\t" + f"• {notacao_z_sup}$={z_alpha_sup:.3f}$" + "\n\n"
        texto += "\t" + f"• {notacao_x_inf}$={x_bar_alpha_inf:.03f}$" + "\n"
        texto += "\t" + f"• {notacao_x_sup}$={x_bar_alpha_sup:.03f}$" + "\n\n"

        texto += (
            f"{notacao_x_sup}$-${notacao_x_inf}$=\
                {x_bar_alpha_sup-x_bar_alpha_inf:.03f}$"
            + "\n"
        )
    elif alt_hip == "greater":
        texto += "Valores críticos:" + "\n"
        texto += "\t" + f"• {notacao_z_sup}$={z_alpha_sup:.3f}$" + "\n\n"
        texto += "\t" + f"• {notacao_x_sup}$={x_bar_alpha_sup:.03f}$" + "\n"

    elif alt_hip == "less":
        texto += "Valores críticos:" + "\n"
        texto += "\t" + f"• {notacao_z_inf}$={z_alpha_inf:.3f}$" + "\n\n"
        texto += "\t" + f"• {notacao_x_inf}$={x_bar_alpha_inf:.03f}$" + "\n"

    resolucao.text(0, 1, texto, ha="left", va="top", size=15)


def resumo_metodos_distribuicoes():
    plt.style.use("default")
    line_color = "#5a5da1"
    z_color = "#7d7d7d"
    area_1_color = "#ff7700"
    area_2_color = "#006644"
    area_3_color = "#660058"

    fig = plt.figure(figsize=(8, 30))
    # fig.suptitle("Resumão de estatística", size=24)
    fig.suptitle(
        "Métodos das distribuições de probabilidade", y=0.92, va="center", size=30
    )
    gs = GridSpec(7, 1, hspace=0.5)

    pontos = 1024
    X = {"x": np.linspace(-5, 5, pontos), "ticks": [], "tick_labels": []}
    Y = {"y": norm.pdf(np.linspace(-5, 5, pontos)), "ticks": [], "tick_labels": []}
    plot_config = {"linewidth": 1.5, "linestyle": "-", "color": line_color}

    x_min = X["x"][0]
    x_max = X["x"][-1]
    # p0 = {'x':-.75, 'y':norm.pdf(-.75)}
    p0 = {"x": -1, "y": norm.pdf(-1)}
    pa = {"x": -2, "y": norm.pdf(-2)}
    pb = {"x": 2, "y": norm.pdf(2)}
    x0 = p0["x"]
    y0 = p0["y"]
    xa = pa["x"]
    ya = pa["y"]
    xb = pb["x"]
    yb = pb["y"]

    # pdf plot
    pdf_plot = fig.add_subplot(gs[0])
    title = r"$ pdf(x) : x \rightarrow y $" + "\n(calc. y a partir de x)"
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x0]
    X_["tick_labels"] += [r"$x_0$"]
    Y_["ticks"] += [y0]
    Y_["tick_labels"] += [r"$y_0=pdf(x_0)$"]
    pt = {"x": x0, "y": y0, "color": z_color, "marker": "o", "zorder": 10}
    v_line = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    h_line = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        True,
        plot_config,
        points=[pt],
        v_lines=[v_line],
        h_lines=[h_line],
    )

    # cdf plot
    cdf_plot = fig.add_subplot(gs[1])
    title = (
        r"$ cdf(x) : x \rightarrow A_{(-\infty,x)} $"
        + "\n(calc. área da esquerda = $P(x<x_0)$)"
    )
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x0]
    X_["tick_labels"] += [r"$x_0$"]
    pt = {"x": x0, "y": y0, "color": z_color, "marker": "o", "zorder": 10}
    v_line = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    fill = {
        "x_inf": x_min,
        "x_sup": x0,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$A_0=cdf(x_0)$",
    }
    ant = {
        "text": r"$área=A_0=cdf(x_0)$",
        "xy": (x0 - 0.5, y0 / 4),
        "xycoords": "data",
        "xytext": (-100, 50),
        "textcoords": "offset points",
        "arrowprops": dict(arrowstyle="->", connectionstyle="arc3"),
    }
    populate_graph(
        cdf_plot,
        title,
        X_,
        Y_,
        True,
        plot_config,
        points=[pt],
        v_lines=[v_line],
        fills=[fill],
        annotations=[ant],
        show_legends=True,
    )

    # ppf plot
    ppf_plot = fig.add_subplot(gs[2])
    title = (
        r"$ ppf(A) : A_{(-\infty,x)} \rightarrow x $"
        + "\n(calc. $x_0$ a partir da área da esquerda ou da $P(x<x_0)$)"
    )
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x0]
    X_["tick_labels"] += [r"$x_0=ppf(A_0)$"]
    pt = {"x": x0, "y": y0, "color": z_color, "marker": "o", "zorder": 10}
    v_line = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    fill = {
        "x_inf": x_min,
        "x_sup": x0,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$A_0$",
    }
    ant = {
        "text": r"$área=A_0$",
        "xy": (x0 - 0.5, y0 / 4),
        "xycoords": "data",
        "xytext": (-100, 50),
        "textcoords": "offset points",
        "arrowprops": dict(arrowstyle="->", connectionstyle="arc3"),
    }
    populate_graph(
        ppf_plot,
        title,
        X_,
        Y_,
        True,
        plot_config,
        points=[pt],
        v_lines=[v_line],
        fills=[fill],
        annotations=[ant],
        show_legends=True,
    )

    # sf plot
    sf_plot = fig.add_subplot(gs[3])
    title = (
        r"$ sf(x) : x \rightarrow A_{(x,+\infty)} $"
        + "\n(calc. área da direita = $P(x>x_0)$)"
    )
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x0]
    X_["tick_labels"] += [r"$x_0$"]
    pt = {"x": x0, "y": y0, "color": z_color, "marker": "o", "zorder": 10}
    v_line = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    fill = {
        "x_inf": x0,
        "x_sup": x_max,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$A_1=sf(x_0)$",
    }
    ant = {
        "text": r"$área=A_1=sf(x_0)$",
        "xy": (x0 + 1, y0 / 2),
        "xycoords": "data",
        "xytext": (50, 50),
        "textcoords": "offset points",
        "arrowprops": dict(arrowstyle="->", connectionstyle="arc3"),
    }
    populate_graph(
        sf_plot,
        title,
        X_,
        Y_,
        True,
        plot_config,
        points=[pt],
        v_lines=[v_line],
        fills=[fill],
        annotations=[ant],
        show_legends=True,
    )

    # isf plot
    isf_plot = fig.add_subplot(gs[4])
    title = (
        r"$ isf(A) : A_{(x,+\infty)} \rightarrow x $"
        + "\n(calc. $x_0$ a partir da área da direita ou da $P(x>x_0)$)"
    )
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x0]
    X_["tick_labels"] += [r"$x_0=isf(A_1)$"]
    pt = {"x": x0, "y": y0, "color": z_color, "marker": "o", "zorder": 10}
    v_line = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    fill = {
        "x_inf": x0,
        "x_sup": x_max,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$A_1$",
    }
    ant = {
        "text": r"$área=A_1$",
        "xy": (x0 + 1, y0 / 2),
        "xycoords": "data",
        "xytext": (50, 50),
        "textcoords": "offset points",
        "arrowprops": dict(arrowstyle="->", connectionstyle="arc3"),
    }
    populate_graph(
        isf_plot,
        title,
        X_,
        Y_,
        True,
        plot_config,
        points=[pt],
        v_lines=[v_line],
        fills=[fill],
        annotations=[ant],
        show_legends=True,
    )

    # interval plot
    interval_plot = fig.add_subplot(gs[5])
    title = r"$ interval(A) : A_{(x_{inf},x_{sup})} \rightarrow (x_{inf}, x_{sup}) $"
    title += "\ncalc. os limites $x_0$ e $x_1$ a partir da área $A_c$"
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [xa, xb]
    X_["tick_labels"] += [r"$x_0=interval(A_c)[0]$", r"$x_1=interval(A_c)[1]$"]
    pt1 = {"x": xa, "y": ya, "color": z_color, "marker": "o", "zorder": 10}
    pt2 = {"x": xb, "y": yb, "color": z_color, "marker": "o", "zorder": 10}
    v_line1 = {"x": xa, "y": ya, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line2 = {"x": xb, "y": yb, "color": z_color, "linewidth": 1, "linestyle": "--"}
    fill = {
        "x_inf": xa,
        "x_sup": xb,
        "color": area_3_color,
        "alpha": 0.25,
        "label": r"$A_c$",
    }
    ant = {
        "text": r"$área=A_c=P(x_0<x<x_1)$",
        "xy": (0, Y["y"][pontos // 2] / 3),
        "xycoords": "data",
        "xytext": (50, 50),
        "textcoords": "offset points",
        "arrowprops": dict(arrowstyle="->", connectionstyle="arc3"),
    }
    populate_graph(
        interval_plot,
        title,
        X_,
        Y_,
        True,
        plot_config,
        points=[pt1, pt2],
        v_lines=[v_line1, v_line2],
        fills=[fill],
        annotations=[ant],
        show_legends=True,
    )

    # summary plot
    summ_plot = fig.add_subplot(gs[6])
    title = r"misturando tudo"
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x0]
    X_["tick_labels"] += [r"$x_0=ppf(A_0)=isf(A_1)$"]
    Y_["ticks"] += [y0]
    Y_["tick_labels"] += [r"$y_0=pdf(x_0)$"]
    pt = {"x": x0, "y": y0, "color": z_color, "marker": "o", "zorder": 10}
    v_line = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    h_line = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    fill_cdf = {
        "x_inf": x_min,
        "x_sup": x0,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$A_0=cdf(x_0)=1-A_1$",
    }
    ant_cdf = {
        "text": r"$A_0=cdf(x_0)=1-A_1$",
        "xy": (x0 - 0.5, y0 / 4),
        "xycoords": "data",
        "xytext": (-100, 50),
        "textcoords": "offset points",
        "arrowprops": dict(arrowstyle="->", connectionstyle="arc3"),
    }
    fill_sf = {
        "x_inf": x0,
        "x_sup": x_max,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$A_1=sf(x_0)=1-A_0$",
    }
    ant_sf = {
        "text": r"$A_1=sf(x_0)=1-A_0$",
        "xy": (x0 + 1, y0 / 2),
        "xycoords": "data",
        "xytext": (50, 50),
        "textcoords": "offset points",
        "arrowprops": dict(arrowstyle="->", connectionstyle="arc3"),
    }
    populate_graph(
        summ_plot,
        title,
        X_,
        Y_,
        True,
        plot_config,
        points=[pt],
        v_lines=[v_line],
        h_lines=[h_line],
        fills=[fill_cdf, fill_sf],
        annotations=[ant_cdf, ant_sf],
        show_legends=True,
    )


def resumo_teste_hipoteses(loose=True):
    plt.style.use("default")
    line_color = "#5a5da1"
    z_color = "#7d7d7d"
    area_1_color = "#ff7700"
    area_2_color = "#006644"
    # area_3_color = "#660058"

    fig = plt.figure(figsize=(25, 25), dpi=300)
    fig.suptitle("Teste de hipótese para média", y=0.95, va="center", size=48)
    gs = GridSpec(7, 4, hspace=0.3)

    pontos = 1024
    X = {"x": np.linspace(-5, 5, pontos), "ticks": [], "tick_labels": []}
    Y = {"y": norm.pdf(np.linspace(-5, 5, pontos)), "ticks": [], "tick_labels": []}
    plot_config = {"linewidth": 1.5, "linestyle": "-", "color": line_color}

    x_min = X["x"][0]
    x_max = X["x"][-1]
    p0 = {"x": -1.5, "y": norm.pdf(-1.5)}
    p1 = {"x": 1.5, "y": norm.pdf(1.5)}
    p_pos = {"x": 0.8, "y": norm.pdf(0.8)}
    p_neg = {"x": 2.2, "y": norm.pdf(2.2)}
    x0 = p0["x"]
    y0 = p0["y"]
    x1 = p1["x"]
    y1 = p1["y"]
    xp = p_pos["x"]
    yp = p_pos["y"]
    xn = p_neg["x"]
    yn = p_neg["y"]

    headers_font_size = 20

    # Dist plot
    pdf_plot = fig.add_subplot(gs[0, 0])
    title = r"$ PDF $"
    X_, Y_ = copy_xy(X, Y)
    fill = {
        "x_inf": x_min,
        "x_sup": x_max,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$A=1$",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        fills=[fill],
        show_legends=True,
    )

    # Col 1 text
    col_1 = fig.add_subplot(gs[0, 1])
    col_1.spines["right"].set_color("none")
    col_1.spines["top"].set_color("none")
    col_1.spines["bottom"].set_color("none")
    col_1.spines["left"].set_color("none")
    col_1.xaxis.set_visible(False)
    col_1.yaxis.set_visible(False)
    texto = (r"$H_0: \mu\leq\mu_0$" + "\n") if loose else (r"$H_0: \mu=\mu_0$" + "\n")
    texto += r"$H_1: \mu>\mu_0$" + "\n\n"
    texto += r"Rejeito $H_0$ se:" + "\n"
    texto += r"$Z>Z_{\alpha}$" + "\nou\n"
    texto += r"$p<\alpha$" + "\n\n"
    col_1.text(0.5, 0.5, texto, ha="center", va="center", size=headers_font_size)

    # Col 2 text
    col_2 = fig.add_subplot(gs[0, 2])
    col_2.spines["right"].set_color("none")
    col_2.spines["top"].set_color("none")
    col_2.spines["bottom"].set_color("none")
    col_2.spines["left"].set_color("none")
    col_2.xaxis.set_visible(False)
    col_2.yaxis.set_visible(False)
    texto = r"$H_0: \mu=\mu_0$" + "\n"
    texto += r"$H_1: \mu\neq\mu_0$" + "\n\n"
    texto += r"Rejeito $H_0$ se:" + "\n"
    texto += r"$|Z|>Z_{\alpha/2}$" + "\nou\n"
    texto += r"$p<\alpha$" + "\n\n"
    col_2.text(0.5, 0.5, texto, ha="center", va="center", size=headers_font_size)

    # Col 3 text
    col_3 = fig.add_subplot(gs[0, 3])
    col_3.spines["right"].set_color("none")
    col_3.spines["top"].set_color("none")
    col_3.spines["bottom"].set_color("none")
    col_3.spines["left"].set_color("none")
    col_3.xaxis.set_visible(False)
    col_3.yaxis.set_visible(False)
    texto = (r"$H_0: \mu\geq\mu_0$" + "\n") if loose else (r"$H_0: \mu=\mu_0$" + "\n")
    texto += r"$H_1: \mu<\mu_0$" + "\n\n"
    texto += r"Rejeito $H_0$ se:" + "\n"
    texto += r"$Z<-Z_{\alpha}$" + "\nou\n"
    texto += r"$p<\alpha$" + "\n\n"
    col_3.text(0.5, 0.5, texto, ha="center", va="center", size=headers_font_size)

    ###################################

    # Linha 1 - confiança
    l1 = fig.add_subplot(gs[1, 0])
    l1.spines["right"].set_color("none")
    l1.spines["top"].set_color("none")
    l1.spines["bottom"].set_color("none")
    l1.spines["left"].set_color("none")
    l1.xaxis.set_visible(False)
    l1.yaxis.set_visible(False)
    texto = r"$signif = \alpha$" + "\n"
    texto += r"$conf = 1-\alpha$" + "\n\n"
    texto += "signif = área verde" + "\n"
    texto += "conf = área laranja" + "\n"
    l1.text(0.5, 0.5, texto, ha="center", va="center", size=headers_font_size)

    # Conf. unicaudal plot le
    pdf_plot_le = fig.add_subplot(gs[1, 1])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x1]
    X_["tick_labels"] += [r"$Z_\alpha$"]
    v_line = {"x": x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    c_fill = {
        "x_inf": x_min,
        "x_sup": x1,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf$",
    }
    s_fill = {
        "x_inf": x1,
        "x_sup": x_max,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    populate_graph(
        pdf_plot_le,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line],
        fills=[c_fill, s_fill],
        show_legends=True,
    )

    # Conf. unicaudal plot ge
    pdf_plot_ge = fig.add_subplot(gs[1, 3])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [-x1]
    X_["tick_labels"] += [r"$-Z_\alpha$"]
    v_line = {"x": -x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    c_fill = {
        "x_inf": -x1,
        "x_sup": x_max,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf$",
    }
    s_fill = {
        "x_inf": x_min,
        "x_sup": -x1,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    populate_graph(
        pdf_plot_ge,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line],
        fills=[c_fill, s_fill],
        show_legends=True,
    )

    # Conf. bicaudal plot
    pdf_plot = fig.add_subplot(gs[1, 2])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x0, x1]
    X_["tick_labels"] += [r"$-Z_{\alpha/2}$", r"$Z_{\alpha/2}$"]
    v_line_0 = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_1 = {"x": x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    c_fill = {
        "x_inf": x0,
        "x_sup": x1,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf.$",
    }
    s_fill_1 = {
        "x_inf": x_min,
        "x_sup": x0,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    s_fill_2 = {"x_inf": x1, "x_sup": x_max, "color": area_2_color, "alpha": 0.25}
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line_0, v_line_1],
        fills=[c_fill, s_fill_1, s_fill_2],
        show_legends=True,
    )

    ###################################

    # Linha 2 - teste Z positivo
    l2 = fig.add_subplot(gs[2, 0])
    l2.spines["right"].set_color("none")
    l2.spines["top"].set_color("none")
    l2.spines["bottom"].set_color("none")
    l2.spines["left"].set_color("none")
    l2.xaxis.set_visible(False)
    l2.yaxis.set_visible(False)
    texto = "Z está dentro do\n intervalo de confiança\n\n"
    texto += r"$\therefore\;aceito\;H_0$"
    l2.text(0.5, 0.5, texto, ha="center", va="center", size=headers_font_size)

    # Unicaudal Z positivo plot le
    pdf_plot = fig.add_subplot(gs[2, 1])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x1, xp]
    X_["tick_labels"] += [r"$Z_\alpha$", r"$Z$"]
    v_line = {"x": x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_z = {"x": xp, "y": yp, "color": z_color, "linewidth": 1, "linestyle": "--"}
    c_fill = {
        "x_inf": x_min,
        "x_sup": x1,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf$",
    }
    s_fill = {
        "x_inf": x1,
        "x_sup": x_max,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line, v_line_z],
        fills=[c_fill, s_fill],
        show_legends=True,
    )

    # Unicaudal Z positivo plot ge
    pdf_plot = fig.add_subplot(gs[2, 3])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [-x1, -xp]
    X_["tick_labels"] += [r"$-Z_\alpha$", r"$Z$"]
    v_line = {"x": -x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_z = {"x": -xp, "y": yp, "color": z_color, "linewidth": 1, "linestyle": "--"}
    c_fill = {
        "x_inf": -x1,
        "x_sup": x_max,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf$",
    }
    s_fill = {
        "x_inf": x_min,
        "x_sup": -x1,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line, v_line_z],
        fills=[c_fill, s_fill],
        show_legends=True,
    )

    # Bicaudal Z positivo plot
    pdf_plot = fig.add_subplot(gs[2, 2])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x0, x1, xp]
    X_["tick_labels"] += [r"$-Z_{\alpha/2}$", r"$Z_{\alpha/2}$", r"$Z$"]
    v_line_0 = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_1 = {"x": x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_z = {"x": xp, "y": yp, "color": z_color, "linewidth": 1, "linestyle": "--"}
    c_fill = {
        "x_inf": x0,
        "x_sup": x1,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf.$",
    }
    s_fill_1 = {
        "x_inf": x_min,
        "x_sup": x0,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    s_fill_2 = {"x_inf": x1, "x_sup": x_max, "color": area_2_color, "alpha": 0.25}
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line_0, v_line_1, v_line_z],
        fills=[c_fill, s_fill_1, s_fill_2],
        show_legends=True,
    )

    ###################################

    # Linha 3 - teste Z negativo
    l3 = fig.add_subplot(gs[3, 0])
    l3.spines["right"].set_color("none")
    l3.spines["top"].set_color("none")
    l3.spines["bottom"].set_color("none")
    l3.spines["left"].set_color("none")
    l3.xaxis.set_visible(False)
    l3.yaxis.set_visible(False)
    texto = "Z está fora do\n intervalo de confiança\n\n"
    texto += r"$\therefore\;rejeito\;H_0$"
    l3.text(0.5, 0.5, texto, ha="center", va="center", size=headers_font_size)

    # Unicaudal Z negativo plot le
    pdf_plot = fig.add_subplot(gs[3, 1])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x1, xn]
    X_["tick_labels"] += [r"$Z_\alpha$", r"$Z$"]
    v_line = {"x": x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_z = {"x": xn, "y": yn, "color": z_color, "linewidth": 1, "linestyle": "--"}
    c_fill = {
        "x_inf": x_min,
        "x_sup": x1,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf$",
    }
    s_fill = {
        "x_inf": x1,
        "x_sup": x_max,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line, v_line_z],
        fills=[c_fill, s_fill],
        show_legends=True,
    )

    # Unicaudal Z negativo plot ge
    pdf_plot = fig.add_subplot(gs[3, 3])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [-x1, -xn]
    X_["tick_labels"] += [r"$-Z_\alpha$", r"$Z$"]
    v_line = {"x": -x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_z = {"x": -xn, "y": yn, "color": z_color, "linewidth": 1, "linestyle": "--"}
    c_fill = {
        "x_inf": -x1,
        "x_sup": x_max,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf$",
    }
    s_fill = {
        "x_inf": x_min,
        "x_sup": -x1,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line, v_line_z],
        fills=[c_fill, s_fill],
        show_legends=True,
    )

    # Bicaudal Z negativo plot
    pdf_plot = fig.add_subplot(gs[3, 2])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [x0, x1, xn]
    X_["tick_labels"] += [r"$-Z_{\alpha/2}$", r"$Z_{\alpha/2}$", r"$Z$"]
    v_line_0 = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_1 = {"x": x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_z = {"x": xn, "y": yn, "color": z_color, "linewidth": 1, "linestyle": "--"}
    c_fill = {
        "x_inf": x0,
        "x_sup": x1,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf.$",
    }
    s_fill_1 = {
        "x_inf": x_min,
        "x_sup": x0,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    s_fill_2 = {"x_inf": x1, "x_sup": x_max, "color": area_2_color, "alpha": 0.25}
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line_0, v_line_1, v_line_z],
        fills=[c_fill, s_fill_1, s_fill_2],
        show_legends=True,
    )

    ###################################

    # Linha 4 - p-value
    l4 = fig.add_subplot(gs[4, 0])
    l4.spines["right"].set_color("none")
    l4.spines["top"].set_color("none")
    l4.spines["bottom"].set_color("none")
    l4.spines["left"].set_color("none")
    l4.xaxis.set_visible(False)
    l4.yaxis.set_visible(False)
    texto = "p é a prob. de obter um resultado\ntão \
        extremo quanto o observado,\nou mais extremo\n\n"
    texto += "$p = $área hachurada"
    l4.text(0.5, 0.5, texto, ha="center", va="center", size=headers_font_size)

    # p unicaudal plot le
    pdf_plot = fig.add_subplot(gs[4, 1])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [xp]
    X_["tick_labels"] += [r"$Z$"]
    v_line = {"x": xp, "y": yp, "color": z_color, "linewidth": 1, "linestyle": "--"}
    p_fill = {
        "x_inf": xp,
        "x_sup": x_max,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
        "label": "p",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line],
        fills=[p_fill],
        show_legends=True,
    )

    # p unicaudal plot ge
    pdf_plot = fig.add_subplot(gs[4, 3])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [-xp]
    X_["tick_labels"] += [r"$Z$"]
    v_line = {"x": -xp, "y": yp, "color": z_color, "linewidth": 1, "linestyle": "--"}
    p_fill = {
        "x_inf": x_min,
        "x_sup": -xp,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
        "label": "p",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line],
        fills=[p_fill],
        show_legends=True,
    )

    # p bicaudal plot
    pdf_plot = fig.add_subplot(gs[4, 2])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [xp, -xp]
    X_["tick_labels"] += [r"$Z$", r"$-Z$"]
    v_line_p = {"x": xp, "y": yp, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_n = {"x": -xp, "y": yp, "color": z_color, "linewidth": 1, "linestyle": "--"}
    p_p_fill = {
        "x_inf": xp,
        "x_sup": x_max,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
        "label": "p",
    }
    p_n_fill = {
        "x_inf": x_min,
        "x_sup": -xp,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line_p, v_line_n],
        fills=[p_p_fill, p_n_fill],
        show_legends=True,
    )

    ###################################

    # Linha 5 - unicaudal p positive
    l5 = fig.add_subplot(gs[5, 0])
    l5.spines["right"].set_color("none")
    l5.spines["top"].set_color("none")
    l5.spines["bottom"].set_color("none")
    l5.spines["left"].set_color("none")
    l5.xaxis.set_visible(False)
    l5.yaxis.set_visible(False)
    texto = r"$p \geq \alpha$" + "\n"
    texto += r"$(hachurado \geq verde)$" + "\n\n"
    texto += r"$\therefore\;aceito\;H_0$"
    l5.text(0.5, 0.5, texto, ha="center", va="center", size=headers_font_size)

    # unicaudal p positive plot le
    pdf_plot = fig.add_subplot(gs[5, 1])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [xp, x1]
    X_["tick_labels"] += [r"$Z$", r"$Z_\alpha$"]
    v_line = {"x": xp, "y": yp, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_z = {"x": x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    p_fill = {
        "x_inf": xp,
        "x_sup": x_max,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
        "label": "p",
    }
    c_fill = {
        "x_inf": x_min,
        "x_sup": x1,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf$",
    }
    s_fill = {
        "x_inf": x1,
        "x_sup": x_max,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line, v_line_z],
        fills=[p_fill, c_fill, s_fill],
        show_legends=True,
    )

    # unicaudal p positive plot ge
    pdf_plot = fig.add_subplot(gs[5, 3])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [-xp, -x1]
    X_["tick_labels"] += [r"$Z$", r"$-Z_\alpha$"]
    v_line = {"x": -xp, "y": yp, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_z = {"x": -x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    p_fill = {
        "x_inf": x_min,
        "x_sup": -xp,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
        "label": "p",
    }
    c_fill = {
        "x_inf": -x1,
        "x_sup": x_max,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf$",
    }
    s_fill = {
        "x_inf": x_min,
        "x_sup": -x1,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line, v_line_z],
        fills=[p_fill, c_fill, s_fill],
        show_legends=True,
    )

    # bicaudal p positive plot
    pdf_plot = fig.add_subplot(gs[5, 2])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [xp, -xp, x0, x1]
    X_["tick_labels"] += [r"$Z$", r"$-Z$", r"$-Z_{\alpha/2}$", r"$Z_{\alpha/2}$"]
    v_line_p = {"x": xp, "y": yp, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_n = {"x": -xp, "y": yp, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_0 = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_1 = {"x": x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    c_fill = {
        "x_inf": x0,
        "x_sup": x1,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf.$",
    }
    s_fill_1 = {
        "x_inf": x_min,
        "x_sup": x0,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    s_fill_2 = {"x_inf": x1, "x_sup": x_max, "color": area_2_color, "alpha": 0.25}
    p_p_fill = {
        "x_inf": xp,
        "x_sup": x_max,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
        "label": "p",
    }
    p_n_fill = {
        "x_inf": x_min,
        "x_sup": -xp,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line_p, v_line_n, v_line_0, v_line_1],
        fills=[p_p_fill, p_n_fill, c_fill, s_fill_1, s_fill_2],
        show_legends=True,
    )

    ###################################

    # Linha 6 - unicaudal p negative
    l6 = fig.add_subplot(gs[6, 0])
    l6.spines["right"].set_color("none")
    l6.spines["top"].set_color("none")
    l6.spines["bottom"].set_color("none")
    l6.spines["left"].set_color("none")
    l6.xaxis.set_visible(False)
    l6.yaxis.set_visible(False)
    texto = r"$p < \alpha$" + "\n"
    texto += r"$(hachurado < verde)$" + "\n\n"
    texto += r"$\therefore\;rejeito\;H_0$"
    l6.text(0.5, 0.5, texto, ha="center", va="center", size=headers_font_size)

    # unicaudal p negative plot le
    pdf_plot = fig.add_subplot(gs[6, 1])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [xn, x1]
    X_["tick_labels"] += [r"$Z$", r"$Z_\alpha$"]
    v_line = {"x": xn, "y": yn, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_z = {"x": x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    p_fill = {
        "x_inf": xn,
        "x_sup": x_max,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
        "label": "p",
    }
    c_fill = {
        "x_inf": x_min,
        "x_sup": x1,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf$",
    }
    s_fill = {
        "x_inf": x1,
        "x_sup": x_max,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line, v_line_z],
        fills=[p_fill, c_fill, s_fill],
        show_legends=True,
    )

    # unicaudal p negative plot ge
    pdf_plot = fig.add_subplot(gs[6, 3])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [-xn, -x1]
    X_["tick_labels"] += [r"$Z$", r"$-Z_\alpha$"]
    v_line = {"x": -xn, "y": yn, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_z = {"x": -x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    p_fill = {
        "x_inf": x_min,
        "x_sup": -xn,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
        "label": "p",
    }
    c_fill = {
        "x_inf": -x1,
        "x_sup": x_max,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf$",
    }
    s_fill = {
        "x_inf": x_min,
        "x_sup": -x1,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line, v_line_z],
        fills=[p_fill, c_fill, s_fill],
        show_legends=True,
    )

    # bicaudal p negative plot
    pdf_plot = fig.add_subplot(gs[6, 2])
    title = ""
    X_, Y_ = copy_xy(X, Y)
    X_["ticks"] += [xn, -xn, x0, x1]
    X_["tick_labels"] += [r"$Z$", r"$-Z$", r"$-Z_{\alpha/2}$", r"$Z_{\alpha/2}$"]
    v_line_p = {"x": xn, "y": yn, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_n = {"x": -xn, "y": yn, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_0 = {"x": x0, "y": y0, "color": z_color, "linewidth": 1, "linestyle": "--"}
    v_line_1 = {"x": x1, "y": y1, "color": z_color, "linewidth": 1, "linestyle": "--"}
    c_fill = {
        "x_inf": x0,
        "x_sup": x1,
        "color": area_1_color,
        "alpha": 0.25,
        "label": r"$conf.$",
    }
    s_fill_1 = {
        "x_inf": x_min,
        "x_sup": x0,
        "color": area_2_color,
        "alpha": 0.25,
        "label": r"$signif=\alpha$",
    }
    s_fill_2 = {"x_inf": x1, "x_sup": x_max, "color": area_2_color, "alpha": 0.25}
    p_p_fill = {
        "x_inf": xn,
        "x_sup": x_max,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
        "label": "p",
    }
    p_n_fill = {
        "x_inf": x_min,
        "x_sup": -xn,
        "facecolor": "none",
        "alpha": 0.5,
        "hatch": "////",
        "edgecolor": "black",
    }
    populate_graph(
        pdf_plot,
        title,
        X_,
        Y_,
        False,
        plot_config,
        just_x_spline=True,
        v_lines=[v_line_p, v_line_n, v_line_0, v_line_1],
        fills=[p_p_fill, p_n_fill, c_fill, s_fill_1, s_fill_2],
        show_legends=True,
    )


def copy_xy(X, Y):
    X_ = X.copy()
    X_["ticks"] = X_["ticks"].copy()
    X_["tick_labels"] = X_["tick_labels"].copy()
    Y_ = Y.copy()
    Y_["ticks"] = Y_["ticks"].copy()
    Y_["tick_labels"] = Y_["tick_labels"].copy()
    return X_, Y_


def populate_graph(
    ax,
    title="",
    X=None,
    Y=None,
    just_primary_splines=True,
    plot_config=None,
    points=[],
    lines=[],  # noqa: F811
    v_lines=[],
    h_lines=[],
    fills=[],
    annotations=[],
    show_legends=False,
    just_x_spline=False,
):
    def hide_sec_splines(ax):
        ax.patch.set_visible(False)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.spines["bottom"].set_visible(True)
        ax.spines["left"].set_visible(True)

    def hide_3_splines(ax):
        ax.patch.set_visible(False)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.spines["bottom"].set_visible(True)

    if plot_config is None:
        plot_config = {"linewidth": 1.5, "linestyle": "-", "color": "blue"}
    if X is None:
        X = {
            "x": np.linspace(-3, 3, 256),
            "ticks": [-2, -1, 0, 1, 2],
            "tick_labels": [r"-2\sigma", r"-\sigma", r"\mu", r"-\sigma", r"2\sigma"],
        }
    if Y is None:
        Y = {
            "y": norm.pdf(np.linspace(-3, 3, 256)),
            "ticks": [0.25, 0.5, 0.75],
            "tick_labels": [0.25, 0.5, 0.75],
        }

    xs = X["x"]
    ys = Y["y"]
    x_min = xs.min()
    x_max = xs.max()
    y_min = ys.min()
    y_max = ys.max()

    # Add title
    ax.set_title(title)

    # Hide secondary splines if needed
    if just_primary_splines:
        hide_sec_splines(ax)

    # Hide secondary splines if needed
    if just_x_spline:
        hide_3_splines(ax)

    # Set axes ranges
    ax.axis(xmin=x_min, xmax=x_max, ymin=y_min, ymax=1.05 * y_max)

    # Set x ticks
    x_ticks = X["ticks"]
    x_tick_labels = X["tick_labels"]
    ax.set_xticks(x_ticks, minor=False)
    ax.set_xticklabels(x_tick_labels, fontdict=None, minor=False)

    # Set y ticks
    y_ticks = Y["ticks"]
    y_tick_labels = Y["tick_labels"]
    ax.set_yticks(y_ticks, minor=False)
    ax.set_yticklabels(y_tick_labels, fontdict=None, minor=False)

    # Plot the curve
    ax.plot(xs, ys, **plot_config)

    # Plot the points
    for point in points:
        ax.scatter(**point)

    # Map vertical line to normal line:
    for v_line in v_lines:
        x_l = v_line["x"]
        y_l = v_line["y"]
        y0 = y_min
        new_line = v_line.copy()
        new_line["x"] = [x_l, x_l]
        new_line["y"] = [y0, y_l]
        lines = lines + [new_line]

    # Map horizontal line to normal line:
    for h_line in h_lines:
        x_l = h_line["x"]
        y_l = h_line["y"]
        x0 = x_min
        new_line = h_line.copy()
        new_line["x"] = [x0, x_l]
        new_line["y"] = [y_l, y_l]
        lines = lines + [new_line]

    # Plot the lines
    for line in lines:
        x = line.pop("x")
        y = line.pop("y")
        ax.plot(x, y, **line)

    # Plot the fills
    for fill in fills:
        x_inf = fill.pop("x_inf")
        x_sup = fill.pop("x_sup")
        mask = (xs > x_inf) & (xs < x_sup)
        x_filled = xs[mask]
        y_filled = ys[mask]
        ax.fill_between(x_filled, y_filled, **fill)

    # Add legends
    if show_legends:
        ax.legend(loc="upper left")

    # Annotations
    for annotation in annotations:
        text = annotation.pop("text")
        xy = annotation.pop("xy")
        ax.annotate(text, xy, **annotation)
