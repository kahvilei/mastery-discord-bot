class summonerData {
    constructor() {  
        this.summoners = [];
    }

    getAllSummoners() {
        fetch("https://us-central1-summon-cloud.cloudfunctions.net/get_summoner_details?operation=get_all_summoners", {mode: 'no-cors'})
            .then((res) => res.json())
            .then((json) => this.summoners=json)
        return this.summoners;
    }
}

export default summonerData;
