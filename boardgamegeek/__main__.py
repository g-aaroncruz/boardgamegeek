import sys
import argparse
import logging
import click

from boardgamegeek.api import BGGClient, HOT_ITEM_CHOICES
from boardgamegeek import BGGClientLegacy

log = logging.getLogger("boardgamegeek")
log_fmt = "[%(levelname)s] %(message)s"

def brief_game_stats(game):
    try:
        desc = '''"{}",{},{}-{},{},{},{},{},"{}","{}"'''.format(game.name, game.year,
               game.min_players, game.max_players,
               game.playing_time,
               game.rating_average, game.rating_average_weight, game.users_rated,
               " / ".join(game.categories).lower(),
               " / ".join(game.mechanics).lower())

        print >>sys.stderr, "{}".format(desc)
        sys.stdout.flush()
    except Exception as e:
        pass

    return

def init_logging(debug):
    """ 
    log is a global variable in this file
    """
    if debug:
        log_level = logging.DEBUG
    else:
        # make requests shush
        logging.getLogger("requests").setLevel(logging.WARNING)
        log_level = logging.INFO

    log.setLevel(log_level)
    stdout = logging.StreamHandler()
    stdout.setLevel(log_level)

    fmt = logging.Formatter(log_fmt)
    stdout.setFormatter(fmt)
    log.addHandler(stdout)

def progress_cb(items, total):
    log.debug("fetching items: {}% complete".format(items*100/total))

@click.group()
@click.pass_context
@click.option("--debug", default=False, help="Enable debug logging. (default: WARN)")
@click.option("--timeout", default=10, help="Timeout for API operations. (default: 10)")
@click.option("--retries", default=5, help="Number of retries to perform in case of timeout or 'data not ready' API response. (default: 5)")
def cli(ctx, debug, timeout, retries):
    # ensure obj exists in case cli is called by other means
    ctx.ensure_object(dict)
    init_logging(debug)
    ctx.obj['bgg_client'] = BGGClient(timeout=timeout, retries=retries)

@cli.group()
@click.pass_context
def search(ctx):
    pass

@search.command()
@click.pass_context
@click.option("--name", default=None, help="Display user profile stats.", required=True)
def user(ctx, name):
    bgg = ctx.obj["bgg_client"]
    if name:
        userstats = bgg.user(name, progress=progress_cb)
        userstats._format(log)

@search.command()
@click.pass_context
@click.option("--id", default=None, help="Display Game ID.")
@click.option("--name", default=None, help="Display user profile stats.")
@click.option("--most-popular", default=True, help="Select most popular game when searching with '--name'. (Default: True)")
@click.option("--recent", default=None, help="Select most recent game when searching with '--name'. (Default: False)")
@click.option("--comments", default=False, help="Get comments for game.")
@click.option("--stats", default=False, help="Show stats for game.")
def game(ctx, id, name, most_popular, recent, comments, stats):
    bgg = ctx.obj["bgg_client"]
    # XOR --id / --name 
    if (id is None and name is None) or (id is not None and name is not None):
        raise click.UsageError("You must provide either --id or --name to search a game.")

    if id:
        game = bgg.game(game_id=id)
        game._format(log)

    if name:
        # XOR --most-popular / --recent
        if (not most_popular and not recent ) or (most_popular and recent):
            raise click.UsageError("You must provide either --most-popular or --recent to search using a name.")

        choice = "best-rank" if most_popular else "recent"
        game = bgg.game(name, choose="best-rank", comments=comments)
        game._format(log)
    if stats:
        brief_game_stats(game)

@search.command()
@click.pass_context
@click.option("--user", default=None, required=True, help="Username to get collection from.")
@click.option("--own", is_flag=True)
@click.option("--trade", is_flag=True)
@click.option("--want", is_flag=True)
@click.option("--wishlist", is_flag=True)
@click.option("--brief", is_flag=True)
@click.option("--rated", is_flag=True)
@click.option("--played", is_flag=True)
@click.option("--commented", is_flag=True)
@click.option("--wishlistpriority", default=1, help="[1:5]")
@click.option("--preordered", is_flag=True)
@click.option("--wanttoplay", is_flag=True)
@click.option("--wanttobuy", is_flag=True)
@click.option("--prevowned", is_flag=True)
def collection(ctx, user, own, trade, want, wishlist, brief, rated, played, commented, wishlistpriority, preordered, \
               wanttoplay, wanttobuy, prevowned):
    bgg = ctx.obj["bgg_client"]
    collection = bgg.collection(user, own=own, trade=trade, want=want, commented=commented, wishlist=wishlist, wishlist_prio=wishlistpriority, rated=rated, played=played, preordered=preordered, prev_owned=prevowned, want_to_buy=wanttobuy, want_to_play=wanttoplay)
    collection._format(log)


if __name__ == "__main__":
    cli()

#---------------------------------------------------------------------
# REFERENCE CODE for conversion
#---------------------------------------------------------------------
def oldargs():
    p = argparse.ArgumentParser(prog="boardgamegeek")

    p.add_argument("-u", "--user", help="Query by user name")
    p.add_argument("-g", "--game", help="Query by game name")
    p.add_argument("--most-recent", help="get the most recent game when querying by name (default)", action="store_true")
    p.add_argument("--most-popular", help="get the most popular (top ranked) game when querying by name", action="store_true")

    p.add_argument("-i", "--id", help="Query by game id", type=int)
    p.add_argument("--game-stats", help="Return brief statistics about the game")
    p.add_argument("-G", "--guild", help="Query by guild id")
    p.add_argument("-c", "--collection", help="Query user's collection list")
    p.add_argument("-p", "--plays", help="Query user's play list")
    p.add_argument("-P", "--plays-by-game", help="Query a game's plays")
    p.add_argument("-H", "--hot-items", help="List all hot items by type", choices=HOT_ITEM_CHOICES)
    p.add_argument("-S", "--search", help="search and return results")

    p.add_argument("-l", "--geeklist", type=int, help="get geeklist by id")
    p.add_argument("--nocomments", help="disable getting the comments with geeklist", action="store_true")

    p.add_argument("--debug", action="store_true")
    p.add_argument("--retries", help="number of retries to perform in case of timeout or API HTTP 202 code",
                   type=int,
                   default=5)
    p.add_argument("--timeout", help="Timeout for API operations", type=int, default=10)

    args = p.parse_args()

def old_main():
    """
    WIP - commands need to be trasnfered to click format
    """

    if args.guild:
        guild = bgg.guild(args.guild, progress=progress_cb)
        guild._format(log)

    if args.plays:
        plays = bgg.plays(name=args.plays, progress=progress_cb)
        plays._format(log)

    if args.plays_by_game:
        try:
            game_id = int(args.plays_by_game)
        except:
            game_id = bgg.get_game_id(args.plays_by_game)

        plays = bgg.plays(game_id=game_id, progress=progress_cb)
        plays._format(log)

    if args.hot_items:
        hot_items = bgg.hot_items(args.hot_items)
        for item in hot_items:
            item._format(log)
            log.info("")

    if args.search:
        results = bgg.search(args.search)
        for r in results:
            r._format(log)
            log.info("")

    oldbgg = BGGClientLegacy(timeout=args.timeout, retries=args.retries)

    if args.geeklist:
        geeklist = oldbgg.geeklist(args.geeklist, comments=not args.nocomments)
        geeklist._format(log)

    log.info("Name        : {}".format(game.name))
    log.info("Categories  : {}".format(game.categories))
    log.info("Mechanics   : {}".format(game.mechanics))
    log.info("Players     : {}-{}".format(game.min_players, game.max_players))
    log.info("Age         : {}".format(game.min_age))
    log.info("Play time   : {}".format(game.playing_time))
    log.info("Game weight : {}".format(game.rating_average_weight))
    log.info("Score       : {}".format(game.rating_average))
    log.info("Votes       : {}".format(game.users_rated))
    log.info("MY SCORE    : {}".format(my_score))