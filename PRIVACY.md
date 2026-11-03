# Privacy policy — Reels Publisher

*Last updated: November 2, 2026* · [Versión en español](#política-de-privacidad--publicador-de-reels)

**Reels Publisher** is a private, personal tool, part of the open-source project
[reels-engine](https://github.com/licho/reels-engine) (`publish` module). It is used only by its author to upload and
schedule his own videos on his own YouTube channels. It is not a product or service, has no other users and is not
offered to third parties.

- It uses **YouTube API Services**. By using it you agree to the
  [YouTube Terms of Service](https://www.youtube.com/t/terms); see also the
  [Google Privacy Policy](https://policies.google.com/privacy).
- Data used: the channel owner's OAuth token (scope `https://www.googleapis.com/auth/youtube`), used only to upload
  videos and set their title, description, tags and publish date; the authorized channel's name; and the author's own
  videos and texts. It does not read, download, store or share any other user's YouTube data.
- Credentials are stored only on the author's computer or as encrypted secrets in his own GitHub repositories, never in
  the code and never shared. No cookies or analytics.
- Access can be revoked at any time at
  [Google security settings](https://security.google.com/settings/security/permissions); deleting the local folder
  `~/.config/reels-engine/` and the GitHub secret removes all stored credentials.
- Contact: open an issue at [github.com/licho/reels-engine/issues](https://github.com/licho/reels-engine/issues).

---

# Política de privacidad — Publicador de Reels

*Última actualización: 2 de noviembre de 2026*

**Publicador de Reels** es una herramienta personal y privada, parte del proyecto de código abierto
[reels-engine](https://github.com/licho/reels-engine) (módulo `publish`). Su único uso es que su autor suba y programe
sus propios videos en sus propios canales de YouTube. No es un producto ni un servicio, no tiene otros usuarios y no se
ofrece a terceros.

## Uso de los Servicios de API de YouTube

Esta herramienta usa los **Servicios de API de YouTube**. Al usarla, aceptas las
[Condiciones del Servicio de YouTube](https://www.youtube.com/t/terms). Los datos que maneja Google están sujetos a la
[Política de Privacidad de Google](https://policies.google.com/privacy).

## Qué datos usa

- **Token de acceso de OAuth** del propietario del canal, otorgado por él mismo con el permiso
  `https://www.googleapis.com/auth/youtube`. Se usa solo para subir videos y fijar su título, descripción, etiquetas y
  fecha de publicación.
- **Nombre del canal** autorizado, solo para mostrar a qué canal quedó conectada la herramienta.
- **Los videos y textos** que el propio autor sube a su canal.

La herramienta **no** lee, descarga, almacena ni comparte datos de otros usuarios, canales, videos, comentarios o
métricas de YouTube.

## Dónde se guardan

Las credenciales se guardan solo en la computadora del autor (`~/.config/reels-engine/`) o como secreto cifrado en
sus propios repositorios de GitHub. Nunca se incluyen en el código, no se envían a ningún servidor propio y no se
comparten con nadie. No se usan cookies ni analítica.

## Cómo quitar el acceso y borrar los datos

Puedes quitar el acceso en cualquier momento desde la
[página de permisos de seguridad de tu cuenta de Google](https://security.google.com/settings/security/permissions).
Para borrar las credenciales guardadas, basta con eliminar la carpeta `~/.config/reels-engine/` y el secreto
correspondiente en GitHub. La herramienta no conserva copias en ningún otro lugar.

## Contacto

Para dudas sobre esta política, abre un *issue* en [github.com/licho/reels-engine/issues](https://github.com/licho/reels-engine/issues).
