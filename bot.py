import os
import logging
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    def load_dotenv(*args, **kwargs):
        print("Warning: python-dotenv not installed; .env file will be ignored")
import discord
from discord.ext import commands
from data_manager import load_data, save_data

load_dotenv()
logging.basicConfig(
    filename=os.getenv('DEBUG_LOG', 'debug.log'),
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    filemode='a'
)
logger = logging.getLogger(__name__)
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error('DISCORD_TOKEN not configured; set it in your environment or .env file')
    raise SystemExit('Missing DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

def build_category_embed(cat, config=None):
    config = config or {}
    title = config.get('title', cat['name'])
    description = config.get('description', 'Explore cards')
    try:
        color = int(config.get('color', '#ffffff').lstrip('#'), 16)
    except ValueError:
        color = 0xFFFFFF
    embed = discord.Embed(title=title, description=description, color=color)
    thumb = config.get('thumbnail')
    if thumb and thumb.startswith(('http://', 'https://')):
        embed.set_thumbnail(url=thumb)
    else:
        if thumb:
            logger.warning('Invalid thumbnail URL %s', thumb)
    img = config.get('image')
    if img and img.startswith(('http://', 'https://')):
        embed.set_image(url=img)
    else:
        if img:
            logger.warning('Invalid image URL %s', img)
    if config.get('footer'):
        embed.set_footer(text=config['footer'])
    return embed


async def update_claims_message(guild):
    """Update or create the persistent claims summary message."""
    data = load_data()
    settings = data.get('settings', {})
    channel_id = settings.get('claims_channel_id')
    if not channel_id:
        return
    channel = guild.get_channel(int(channel_id))
    if not channel:
        return
    # Build summary
    lines = []
    for cat in data.get('categories', []):
        for card in cat.get('cards', []):
            if card.get('claimed_by'):
                lines.append(f"{card['name']} - {card['claimed_by']}")
    summary = "\n".join(lines) or "No claims yet"
    message_id = settings.get('claims_message_id')
    msg = None
    if message_id:
        try:
            msg = await channel.fetch_message(int(message_id))
            await msg.edit(content=summary)
        except discord.NotFound:
            msg = None
    if msg is None:
        msg = await channel.send(summary)
        settings['claims_message_id'] = str(msg.id)
        save_data(data)

class ExploreView(discord.ui.View):
    def __init__(self, user, cat, grid_size):
        super().__init__(timeout=300)
        self.user = user
        self.cat = cat
        self.index = 0
        self.grid_size = grid_size
        self.per_page = grid_size * grid_size
        logger.debug('Opening ExploreView for %s in category %s', user, cat['id'])
        self.update_children()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id

    def update_children(self):
        self.clear_items()
        logger.debug('Updating ExploreView buttons index=%s', self.index)
        cards = self.cat['cards'][self.index:self.index + self.per_page]
        rows = self.grid_size
        for i, card in enumerate(cards):
            button = discord.ui.Button(label=card['name'], style=discord.ButtonStyle.grey, row=i // rows)
            button.callback = self.make_view_card(card)
            self.add_item(button)
        if self.index > 0:
            prev_btn = discord.ui.Button(label='Prev', style=discord.ButtonStyle.blurple)
            prev_btn.callback = self.prev_page
            self.add_item(prev_btn)
        if self.index + self.per_page < len(self.cat['cards']):
            next_btn = discord.ui.Button(label='Next', style=discord.ButtonStyle.blurple)
            next_btn.callback = self.next_page
            self.add_item(next_btn)

    def make_view_card(self, card):
        async def callback(interaction: discord.Interaction):
            logger.debug('Viewing card %s from category %s', card['id'], self.cat['id'])
            embed = discord.Embed(title=card['name'])
            embed.set_image(url=card['front'])
            view = CardView(self.user, self.cat, card)
            await interaction.response.edit_message(embed=embed, view=view)
        return callback

    async def prev_page(self, interaction: discord.Interaction):
        self.index = max(0, self.index - self.per_page)
        logger.debug('ExploreView prev_page index=%s', self.index)
        self.update_children()
        await interaction.response.edit_message(view=self)

    async def next_page(self, interaction: discord.Interaction):
        self.index += self.per_page
        logger.debug('ExploreView next_page index=%s', self.index)
        self.update_children()
        await interaction.response.edit_message(view=self)

class CardView(discord.ui.View):
    def __init__(self, user, cat, card):
        super().__init__(timeout=300)
        self.user = user
        self.cat = cat
        self.card = card

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id

    @discord.ui.button(label='Left', style=discord.ButtonStyle.secondary)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        logger.debug('Showing back of card %s', self.card['id'])
        embed = discord.Embed(title=self.card['name'])
        embed.set_image(url=self.card['back'])
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Right', style=discord.ButtonStyle.secondary)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        logger.debug('Showing front of card %s', self.card['id'])
        embed = discord.Embed(title=self.card['name'])
        embed.set_image(url=self.card['front'])
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Claim', style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        cat = next((c for c in data['categories'] if c['id'] == self.cat['id']), None)
        card = next((x for x in cat['cards'] if x['id'] == self.card['id']), None)
        if card and not card.get('claimed_by'):
            logger.debug('Card %s claimed by %s', self.card['id'], interaction.user)
            card['claimed_by'] = interaction.user.name
            save_data(data)
            await interaction.response.send_message('Claimed!', ephemeral=True)
            await update_claims_message(interaction.guild)
        else:
            await interaction.response.send_message('Already claimed', ephemeral=True)

    @discord.ui.button(label='Unclaim', style=discord.ButtonStyle.red)
    async def unclaim(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        cat = next((c for c in data['categories'] if c['id'] == self.cat['id']), None)
        card = next((x for x in cat['cards'] if x['id'] == self.card['id']), None)
        if card and card.get('claimed_by') == interaction.user.name:
            logger.debug('Card %s unclaimed by %s', self.card['id'], interaction.user)
            card['claimed_by'] = None
            save_data(data)
            await interaction.response.send_message('Unclaimed', ephemeral=True)
            await update_claims_message(interaction.guild)
        else:
            await interaction.response.send_message('Cannot unclaim', ephemeral=True)

    @discord.ui.button(label='Back', style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        logger.debug('Returning to card list for category %s', self.cat['id'])
        data = load_data()
        grid = data.get('settings', {}).get('grid_size', 3)
        view = ExploreView(self.user, self.cat, grid)
        data = load_data()
        embed = build_category_embed(self.cat, data.get('embed'))
        await interaction.response.edit_message(embed=embed, view=view)

@bot.command()
async def register(ctx):
    logger.debug('Register command invoked by %s', ctx.author)
    data = load_data()
    settings = data.get('settings', {})
    embed_cfg = data.get('embed', {})
    channel = ctx.channel
    if settings.get('inventory_channel_id'):
        chan = ctx.guild.get_channel(int(settings['inventory_channel_id']))
        if chan:
            channel = chan
    claims_chan = None
    if settings.get('claims_channel_id'):
        claims_chan = ctx.guild.get_channel(int(settings['claims_channel_id']))
    for cat in data['categories']:
        embed = build_category_embed(cat, embed_cfg)
        view = discord.ui.View()
        label = embed_cfg.get('button_label', 'Explore')
        view.add_item(discord.ui.Button(label=label, custom_id=f'explore_{cat["id"]}'))
        msg = await channel.send(embed=embed, view=view)
        cat['message_id'] = msg.id
    save_data(data)
    await ctx.send('Registration complete.')
    if claims_chan:
        await update_claims_message(ctx.guild)

@bot.event
async def on_ready():
    logger.info('Logged in as %s', bot.user)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom = interaction.data.get('custom_id', '')
        if custom.startswith('explore_'):
            cat_id = custom.split('_', 1)[1]
            logger.debug('Explore interaction for category %s by %s', cat_id, interaction.user)
            data = load_data()
            cat = next((c for c in data['categories'] if c['id'] == cat_id), None)
            if not cat:
                logger.debug('Category %s missing for interaction', cat_id)
                await interaction.response.send_message('Category missing', ephemeral=True)
                return
            settings = data.get('settings', {})
            grid = settings.get('grid_size', 3)
            try:
                if interaction.user.is_on_mobile():
                    grid = min(grid, 2)
            except AttributeError:
                pass
            view = ExploreView(interaction.user, cat, grid)
            embed = build_category_embed(cat, data.get('embed'))
            await interaction.response.send_message(embed=embed, ephemeral=True, view=view)

if __name__ == '__main__':
    logger.info('Starting Discord bot')
    bot.run(TOKEN)
