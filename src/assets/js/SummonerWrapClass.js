//TODO summoner wrapper class that grabs data and performs calculations

class Summoner{
    constructor(puuid) {
      this.puuid = puuid;
      this.name = this.name();
    }
    async name() {
        const response = await fetch("https://us-central1-summon-cloud.cloudfunctions.net/summoners_orchestration/get-summoner-field/" + this.puuid + "/name")
                                .then(response => response.json());
        console.log(response);
        return response;
    }
}

export default Summoner;