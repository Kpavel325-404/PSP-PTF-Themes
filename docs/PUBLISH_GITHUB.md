# Publishing on GitHub / Загрузка на GitHub

Extract the archive and open PSP-PTF-Themes. Its contents form the repository root.

## New repository

Create an empty **PSP-PTF-Themes** repository on Kpavel325-404 and choose the visibility you want. README, .gitignore and scoped licensing files are already supplied.

[Prefilled repository form](https://github.com/new?name=PSP-PTF-Themes&owner=Kpavel325-404)

From inside the extracted directory:

~~~sh
git init -b main
git add .
git commit -m "Add nine PSP PTF themes with previews and verification"
git remote add origin https://github.com/Kpavel325-404/PSP-PTF-Themes.git
git push -u origin main
~~~

Use your existing Git identity/authentication. These commands assume a new empty repository. For an existing project, place the files in its checkout and follow its usual commit process.

The supplied Actions workflow checks original hashes, structure, 661 graphics, packaged hashes and documentation links. Confirm its first successful remote run.

## Presentation

Suggested description:

> Nine native PSP PTF themes: retro Windows and Mac, Frutiger glass, Eesti Retro and Winter Moscow. Previews, source assets and reproducible desktop verification.

Suggested topics: psp, ptf, themes, xmb, frutiger-aero, frutiger-aqua, retrocomputing.

Use assets/social-preview.png for the social preview: 1280 × 640, below 1 MB. Release text is ready in [RELEASE_NOTES.md](RELEASE_NOTES.md). A release may attach this ZIP, individual themes and checksums with their exact version and testing status.

## По-русски

Загрузи содержимое PSP-PTF-Themes в отдельный репозиторий. README.md должен оказаться в корне; включи папку .github. Обложка — assets/social-preview.png, текст релиза — docs/RELEASE_NOTES.md. После загрузки проверь Actions. Аппаратные результаты отмечай по реальным испытаниям.

[GitHub: create repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository) · [Push](https://docs.github.com/en/get-started/using-git/pushing-commits-to-a-remote-repository) · [Social preview](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview) · [Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
