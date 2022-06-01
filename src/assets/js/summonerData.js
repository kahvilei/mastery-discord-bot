
export async function summonerList() {
        const response = await fetch("https://us-central1-summon-cloud.cloudfunctions.net/get_summoner_details?operation=get_all_summoners")
                               .then(response => response.json());

        console.log(response);
        return response;
}
