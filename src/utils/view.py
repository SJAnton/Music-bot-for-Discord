import discord
from utils.embed import queue_embed

class QueueView(discord.ui.View):
    def __init__(self, queue, jump, init_msg, *, timeout=180):
        super().__init__(timeout=timeout)

        self.queue = queue
        self.first = 0
        self.jump = jump
        self.init_msg = init_msg
        self.update_buttons()

    def update_buttons(self):
        for item in self.children:
            if not isinstance(item, discord.ui.Button):
                continue
            elif str(item.emoji) == "⬅️":
                item.disabled = self.first == 0
            elif str(item.emoji) == "➡️":
                item.disabled = self.first + self.jump >= len(self.queue)

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.first -= self.jump
        self.update_buttons()
        await interaction.response.edit_message(
            embed=queue_embed(self.queue, self.first, self.first + self.jump, self.init_msg),
            view=self
        )
    
    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.first += self.jump
        self.update_buttons()
        await interaction.response.edit_message(
            embed=queue_embed(self.queue, self.first, self.first + self.jump, self.init_msg),
            view=self
        )
