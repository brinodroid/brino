
import { getBackend } from './Backend';

class WatchListCache {
  constructor() {

    if (WatchListCache.instance) {
      return WatchListCache.instance;
    }

    this.watchListMap = {}
    this.watchList = [];

    this.isCached = this.isCached.bind(this);
    this.getWatchList = this.getWatchList.bind(this);
    this.getWatchListTicker = this.getWatchListTicker.bind(this);
    this.loadWatchList = this.loadWatchList.bind(this);

    WatchListCache.instance = this;

    return WatchListCache.instance;

  }

  isCached() {
    return this.watchList.length > 0;
  }

  getWatchList() {
    return this.watchList;
  }

  getWatchListTicker(watchlistId) {
    let watchListItem = this.watchListMap[watchlistId];
    let watchListTicker = '';
    console.info("getWatchListTicker: item: %o", watchListItem);
    if (!watchListItem) {
      watchListTicker = 'NOT FOUND. Stale?';
    } else if (watchListItem.asset_type === 'STOCK') {
      watchListTicker = watchListItem.ticker;
    } else {
      // Its an option
      watchListTicker = watchListItem.ticker + ' ' + watchListItem.asset_type + ' ' + watchListItem.option_strike + ' ' + watchListItem.option_expiry;
    }
    return watchListTicker;
  }

  loadWatchList(watchlistLoadedCallback) {
    console.info('loadWatchList: Loading watchlist...')
    let loadWatchListCallback = function (httpStatus, json) {
      if (httpStatus === 401) {
        console.error("loadWatchListCallback: authentication expired?");
        if (watchlistLoadedCallback) {
          watchlistLoadedCallback(httpStatus, "Authentication expired?");
        }

        return;
      }

      if (httpStatus !== 200) {
        console.error("loadWatchListCallback: failure: http:%o", httpStatus);

        if (watchlistLoadedCallback) {
          watchlistLoadedCallback(httpStatus, "Failed to load watchlist");
        }
        return;
      }

      // Converting watchList json array to a map
      console.info("loadWatchListCallback: json: %o", json);
      this.watchList = json;
      this.watchListMap = json.reduce(function (map, obj) {
        map[obj.id] = obj;
        return map;
      }, {});

      if (watchlistLoadedCallback) {
        watchlistLoadedCallback(httpStatus, json);
      }
    }

    getBackend().getWatchList(loadWatchListCallback.bind(this));
  }
}

const watchlistCache = new WatchListCache();

export default watchlistCache;