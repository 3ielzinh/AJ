/* main.js — Scripts globais do projeto AJ */
(function () {
    "use strict";

    // ── Menu mobile ──────────────────────────────────────────────────────
    var toggle = document.getElementById("menu-toggle");
    var nav    = document.getElementById("main-nav");

    if (toggle && nav) {
        toggle.addEventListener("click", function () {
            var isOpen = nav.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", isOpen);
        });

        // Fecha ao clicar fora
        document.addEventListener("click", function (e) {
            if (!toggle.contains(e.target) && !nav.contains(e.target)) {
                nav.classList.remove("is-open");
                toggle.setAttribute("aria-expanded", "false");
            }
        });
    }

    // ── Fechar alertas ────────────────────────────────────────────────────
    document.querySelectorAll(".alert-close").forEach(function (btn) {
        btn.addEventListener("click", function () {
            btn.closest(".alert").remove();
        });
    });

    // ── Barra de progresso em navegações e submits ──────────────────────
    var bar = document.getElementById("aj-progress");
    if (bar) {
        function showProgress() {
            bar.style.width = "0%";
            bar.classList.add("active");
            var w = 0;
            var iv = setInterval(function () {
                w = w < 80 ? w + Math.random() * 10 : w;
                bar.style.width = w + "%";
            }, 200);
            window.addEventListener("load", function () {
                clearInterval(iv);
                bar.style.width = "100%";
                setTimeout(function () { bar.classList.remove("active"); bar.style.width = "0%"; }, 300);
            }, { once: true });
        }

        // Links de navegação
        document.querySelectorAll("a[href]").forEach(function (a) {
            if (a.hostname === location.hostname && !a.hasAttribute("download")) {
                a.addEventListener("click", showProgress);
            }
        });

        // Formulários
        document.querySelectorAll("form").forEach(function (form) {
            form.addEventListener("submit", function () {
                showProgress();
                var submit = form.querySelector("[type='submit']");
                if (submit) submit.classList.add("is-loading");
            });
        });
    }
})();
