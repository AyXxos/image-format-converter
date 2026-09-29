from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk


class ConvertisseurApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Convertisseur d'Images")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        self.fichier_actuel: Path | None = None
        self.image_preview: ImageTk.PhotoImage | None = None

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
            text="Convertisseur d'Images Express",
            style="Header.TLabel",
        )
        header.pack(pady=15)

        # Zone Sélection & Aperçu
        frame_fichier = ttk.LabelFrame(
            self.root, text=" Fichier source ", padding=10
        )
        frame_fichier.pack(fill="x", padx=20, pady=5)

        btn_parcourir = ttk.Button(
            frame_fichier,
            text="Choisir une image...",
            command=self.charger_image,
        )
        btn_parcourir.pack(anchor="w", pady=5)

        self.lbl_chemin = ttk.Label(
            frame_fichier, text="Aucun fichier sélectionné", foreground="gray"
        )
        self.lbl_chemin.pack(anchor="w")

        # Cadre d'aperçu
        self.lbl_preview = ttk.Label(
            frame_fichier,
            text="Aperçu indisponible",
            background="#f0f0f0",
            anchor="center",
        )
        self.lbl_preview.pack(fill="x", pady=10, ipady=30)

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

        # Action & Progression
        self.btn_convertir = ttk.Button(
            self.root,
            text="Convertir l'image",
            command=self.convertir,
            state="disabled",
        )
        self.btn_convertir.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, mode="determinate")
        self.progress.pack(fill="x", padx=20, pady=5)

    def _update_label_qualite(self, val):
        self.lbl_qualite_val.config(text=f"{int(float(val))} %")

    def charger_image(self):
        path = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=[
                (
                    "Images",
                    "*.png *.jpg *.jpeg *.webp *.bmp *.gif",
                ),
                ("Tous les fichiers", "*.*"),
            ],
        )
        if not path:
            return

        self.fichier_actuel = Path(path)
        self.lbl_chemin.config(
            text=f"Fichier : {self.fichier_actuel.name}", foreground="black"
        )

        # Génération d'un vignette d'aperçu
        try:
            with Image.open(self.fichier_actuel) as img:
                img.thumbnail((200, 120))
                self.image_preview = ImageTk.PhotoImage(img)
                self.lbl_preview.config(image=self.image_preview, text="")
            self.btn_convertir.config(state="normal")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lire l'image : {e}")

    def convertir(self):
        if not self.fichier_actuel:
            return

        format_cible = self.var_format.get().lower()
        qualite = self.var_qualite.get()

        fichier_sortie = filedialog.asksaveasfilename(
            defaultextension=f".{format_cible}",
            initialfile=f"{self.fichier_actuel.stem}.{format_cible}",
            filetypes=[(f"Image {format_cible.upper()}", f"*.{format_cible}")],
        )

        if not fichier_sortie:
            return

        self.progress["value"] = 30
        self.root.update_idletasks()

        try:
            with Image.open(self.fichier_actuel) as img:
                # Gestion du mode couleur selon le format cible (transparence RGBA -> RGB)
                if format_cible in ["jpeg", "jpg"] and img.mode in (
                    "RGBA",
                    "P",
                ):
                    img = img.convert("RGB")

                self.progress["value"] = 70
                self.root.update_idletasks()

                img.save(
                    fichier_sortie,
                    format=format_cible.upper(),
                    subsampling=0,
                    quality=qualite,
                    optimize=True,
                )

            self.progress["value"] = 100
            messagebox.showinfo(
                "Succès", f"Fichier enregistré :\n{fichier_sortie}"
            )
        except Exception as e:
            messagebox.showerror("Erreur de conversion", str(e))
        finally:
            self.progress["value"] = 0


if __name__ == "__main__":
    root = tk.Tk()
    app = ConvertisseurApp(root)
    root.mainloop()