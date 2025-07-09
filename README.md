# Discord Trading Card Bot

This project contains a basic Discord bot and a web-based admin UI for managing trading card inventory.

## Features
- Register as a seller and choose Discord channels used for inventory listings and claims.
- Add categories and trading cards via a web interface.
- Each category is announced with an embed containing an **Explore** button.
- Users can browse cards in an ephemeral message grid (3x3 on desktop, 2x2 on mobile).
- Cards include front/back images and can be claimed or unclaimed.
- Batch add cards with paired front/back images.
- Customize embed title, description, button text, color, images and footer via the Embed Builder tab with a live preview.
- Delete categories and cards directly from the admin pages.
- Admin options are organized into tabs for clarity.
- Configure channel IDs and grid size from the new **Settings** tab.

## Setup
1. Create a Discord application and bot, then obtain your token.
2. Clone this repository and install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
   If you see `ModuleNotFoundError: No module named 'dotenv'`, ensure the
   `python-dotenv` package was installed by running the command above.
3. Copy `example.env` to `.env` and fill in your Discord bot token and preferred settings. If no `ADMIN_PASSWORD` is defined, the default login password is `change-me`.
4. Run the web app and bot in separate terminals:
   ```bash
   python app.py
   ```
   ```bash
   python bot.py
   ```

Use the **Settings** tab in the admin UI to set the channel IDs used for
inventory messages, claims updates and the image dump. You can also adjust the
grid size used when browsing cards.

The bot reads configuration from `.env` and `data/inventory.json`.

Use the tabs at the top of the admin UI to switch between inventory management and the embed builder preview.

All server and bot actions are logged to `debug.log` in the project root. Check
this file when troubleshooting.

## Notes
This is a starting point and does not include advanced authentication or hosting setup. Add your own enhancements as needed.
