# l5r-discord-bot
A bot for the [L5R Discord](https://discord.gg/zPvBePb).

It can apply default roles to new members, roll dice (for the L5R 4e RPG) and allow users to join and leave roles on the server.

The syntax is as follows:

```
!help provides a help text.

clan <rolename> lets you swear allegiance to or leave a given clan.

!clan <rolename> default lets the admins set default roles that to apply to new members. 

!clans tells you how many people are in each clan.

[] denotes optional elements, {} denotes 'pick one'. show_dice shows the individual dice results.
!roll XkY [{+-}Z} [TN##] [unskilled] [emphasis] [mastery] [show_dice] rolls X 10-sided exploding dice and keeps the highest Y.
Unskilled can be set to prevent the dice from exploding, while Emphasis rerolls 1s.
Mastery allows the dice to explode on 9s and 10s.
Ex. !roll 6k3 TN20 or !roll 2k2 TN10 unskilled

```
