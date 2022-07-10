//TODO summoner wrapper class that grabs data and performs calculations
import Summoner from './SummonerClass.js';

class SummonerList{
    constructor(summoners) {
        if (typeof summoners === 'undefined') {
            throw new Error('Cannot be called directly or without a suitable list');
        }
        this.list = summoners;
    }

    static async build(sort = "name", filter = "") {
        var sortRefined = sort.replace(' ', '_').toLowerCase();
        if (filter != ""){
            sortRefined += "_" + filter
        }
        var rawList = await this.pullRawSummonerList(sortRefined, filter);
        var summonerArray = []
        var counter = 0;
        rawList.map((summoner) => {
            summonerArray[counter] = new Summoner(summoner);
            counter += 1;
        })

        return new SummonerList(summonerArray);
    }

    static async pullRawSummonerList(sort) {
        const response = await fetch("https://us-central1-summon-cloud.cloudfunctions.net/summoners_orchestration/get-all-summoners/sort/" + sort)
                                .then(response => response.json());

        return response;
    }
}

export default SummonerList;