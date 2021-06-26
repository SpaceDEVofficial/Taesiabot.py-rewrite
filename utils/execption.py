from discord.ext import commands
class PermError:
    class BlacklistedUser(commands.CheckFailure):
        def __str__(self):
            return "BlackListed User"

    class NotOwnerUser(commands.CheckFailure):
        def __str__(self):
            return "This user is not owner"