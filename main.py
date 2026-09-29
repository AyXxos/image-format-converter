from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image


class ConvertisseurBatchApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Convertisseur d'Images en Lot")
        self.root.geometry("620x580")
        self.root.resizable(False, False)

        self.fichiers_charges: list[Path] = []

        self._creer_style()
        self._creer_widgets()

    def _creer_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 10), padding=6)
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure(
            "Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#2c3e50"
        )

    def _creer_widgets(self):
        # En-tête
        header = ttk.Label(
            self.root,
            text="Convertisseur d'Images en Lot",
            style="Header.TLabel",
        )
        header.pack(pady=15)

        # Zone Sélection
        frame_fichier = ttk.LabelFrame(
            self.root, text=" Images sources ", padding=10
        )
        frame_fichier.pack(fill="x", padx=20, pady=5)

        btn_box = ttk.Frame(frame_fichier)
        btn_box.pack(fill="x", pady=5)

        btn_fichiers = ttk.Button(
            btn_box,
            text="Choisir des fichiers...",
            command=self.charger_fichiers,
        )
        btn_fichiers.pack(side="left", padx=5)

        btn_dossier = ttk.Button(
            btn_box, text="Choisir un dossier...", command=self.charger_dossier
        )
        btn_dossier.pack(side="left", padx=5)

        # Liste affichant les fichiers sélectionnés
        self.listbox = tk.Listbox(
            frame_fichier, height=6, selectmode=tk.EXTENDED
        )
        self.listbox.pack(fill="x", pady=5)

        self.lbl_compteur = ttk.Label(
            frame_fichier, text="Aucun fichier sélectionné", foreground="gray"
        )
        self.lbl_compteur.pack(anchor="w")

        # Options de conversion
        frame_options = ttk.LabelFrame(
            self.root, text=" Options de sortie ", padding=10
        )
        frame_options.pack(fill="x", padx=20, pady=10)

        # Format
        ttk.Label(frame_options, text="Format cible :").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.var_format = tk.StringVar(value="WEBP")
        combo_format = ttk.Combobox(
            frame_options,
            textvariable=self.var_format,
            values=["WEBP", "PNG", "JPEG", "BMP"],
            state="readonly",
            width=10,
        )
        combo_format.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Qualité
        ttk.Label(frame_options, text="Qualité :").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.var_qualite = tk.IntVar(value=85)
        scale_qualite = ttk.Scale(
            frame_options,
            from_=1,
            to=100,
            variable=self.var_qualite,
            command=self._update_label_qualite,
        )
        scale_qualite.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self.lbl_qualite_val = ttk.Label(frame_options, text="85 %")
        self.lbl_qualite_val.grid(row=1, column=2, sticky="w", padx=5)

        # Bouton Action
        self.btn_convertir = ttk.Button(
            self.root,
            text="Tout convertir",
            command=self.convertir_tout,
            state="disabled",
        )
        self.btn_convertir.pack(pady=10)

        # Zone de Progression dédiée
        frame_progression = ttk.Frame(self.root)
        frame_progression.pack(fill="x", padx=20, pady=5)

        self.lbl_status = ttk.Label(
            frame_progression, text="", font=("Segoe UI", 9, "italic")
        )
        self.lbl_status.pack(anchor="w", pady=(0, 2))

        self.progress = ttk.Progressbar(frame_progression, mode="determinate")
        self.progress.pack(fill="x")

    def _update_label_qualite(self, val):
        self.lbl_qualite_val.config(text=f"{int(float(val))} %")

    def _mettre_a_jour_liste(self):
        self.listbox.delete(0, tk.END)
        for f in self.fichiers_charges:
            self.listbox.insert(tk.END, f.name)

        nb = len(self.fichiers_charges)
        if nb > 0:
            self.lbl_compteur.config(
                text=f"{nb} fichier(s) sélectionné(s)", foreground="black"
            )
            self.btn_convertir.config(state="normal")
        else:
            self.lbl_compteur.config(
                text="Aucun fichier sélectionné", foreground="gray"
            )
            self.btn_convertir.config(state="disabled")

    def charger_fichiers(self):
        paths = filedialog.askopenfilenames(
            title="Sélectionner une ou plusieurs images",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"),
                ("Tous les fichiers", "*.*"),
            ],
        )
        if paths:
            self.fichiers_charges = [Path(p) for p in paths]
            self._mettre_a_jour_liste()

    def charger_dossier(self):
        dossier = filedialog.askdirectory(
            title="Sélectionner un dossier d'images"
        )
        if dossier:
            extensions = ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp")
            fichiers = []
            path_dossier = Path(dossier)
            for ext in extensions:
                fichiers.extend(path_dossier.glob(ext))

            self.fichiers_charges = sorted(fichiers)
            self._mettre_a_jour_liste()

    def convertir_tout(self):
        if not self.fichiers_charges:
            return

        dossier_sortie = filedialog.askdirectory(
            title="Choisir le dossier de destination"
        )
        if not dossier_sortie:
            return

        dest = Path(dossier_sortie)
        format_cible = self.var_format.get().lower()
        qualite = self.var_qualite.get()

        total = len(self.fichiers_charges)

        # Configuration de la barre de progression
        self.progress["maximum"] = total
        self.progress["value"] = 0
        self.btn_convertir.config(state="disabled")

        succes = 0
        erreurs = 0

        for idx, fichier in enumerate(self.fichiers_charges, start=1):
            # Mise à jour du texte de statut et de la barre
            self.lbl_status.config(
                text=f"Traitement : {idx}/{total} ({fichier.name})"
            )
            self.progress["value"] = idx - 1
            self.root.update()  # Forcer le rafraîchissement graphique immédiat

            fichier_sortie = dest / f"{fichier.stem}.{format_cible}"

            try:
                with Image.open(fichier) as img:
                    if format_cible in ["jpeg", "jpg"] and img.mode in (
                        "RGBA",
                        "P",
                    ):
                        img = img.convert("RGB")

                    img.save(
                        fichier_sortie,
                        format=format_cible.upper(),
                        quality=qualite,
                        optimize=True,
                    )
                    succes += 1
            except Exception:
                erreurs += 1

            # Progression de la barre après la sauvegarde de l'image
            self.progress["value"] = idx
            self.root.update()

        # Fin du traitement
        self.lbl_status.config(text="Conversion terminée !", foreground="green")
        self.btn_convertir.config(state="normal")

        msg = f"Conversion terminée !\n\n- {succes} image(s) réussie(s)"
        if erreurs > 0:
            msg += f"\n- {erreurs} échec(s)"

        messagebox.showinfo("Résultat", msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = ConvertisseurBatchApp(root)
    root.mainloop()