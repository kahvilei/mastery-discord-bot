
export async function summonerList() {
    const response = await fetch("https://us-central1-summon-cloud.cloudfunctions.net/orchestration/get-all-summoners")
                            .then(response => response.json());

    console.log(response);
    return response;
}

export async function liveMatches() {
    const response = await fetch("https://us-central1-summon-cloud.cloudfunctions.net/orchestration/get-live-matches")
                           .then(response => response.json());

    console.log(response);
    return response;
}

export const liveData = [
        {
            "gameId": 4326706789,
            "mapId": 11,
            "gameMode": "URF",
            "gameType": "MATCHED_GAME",
            "gameQueueConfigId": 900,
            "keySummoners": ["Snam", "grandtheftodom"],
            "participants": [
                {
                    "teamId": 100,
                    "isKey": true,
                    "spell1Id": 4,
                    "spell2Id": 14,
                    "championId": 105,
                    "profileIconId": 565,
                    "summonerName": "grandtheftodom",
                    "bot": false,
                    "summonerId": "Eny6Z_rz7V4oYwL1cHQFxvqqJhyyaAWyhYNM--4NWAPPQcA",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8128,
                            8143,
                            8138,
                            8105,
                            8014,
                            9111,
                            5008,
                            5008,
                            5002
                        ],
                        "perkStyle": 8100,
                        "perkSubStyle": 8000
                    }
                },
                {
                    "teamId": 100,
                    "isKey": true,
                    "spell1Id": 4,
                    "spell2Id": 6,
                    "championId": 6,
                    "profileIconId": 23,
                    "summonerName": "Snam",
                    "bot": false,
                    "summonerId": "lxCOZHPlnR-2MyoESLs99iFLV_5PMdFT-K1AbnTgRyHvO_0",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8005,
                            9111,
                            9104,
                            8014,
                            8139,
                            8135,
                            5005,
                            5008,
                            5002
                        ],
                        "perkStyle": 8000,
                        "perkSubStyle": 8100
                    }
                },
                {
                    "teamId": 100,
                    "spell1Id": 4,
                    "spell2Id": 7,
                    "championId": 16,
                    "profileIconId": 4022,
                    "summonerName": "Miyak",
                    "bot": false,
                    "summonerId": "7fshguUlCiCBrSHlUOkYEJDhwYGL6A4XvFeAsRIlMbtpdCI",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8214,
                            8224,
                            8210,
                            8237,
                            8473,
                            8453,
                            5008,
                            5008,
                            5002
                        ],
                        "perkStyle": 8200,
                        "perkSubStyle": 8400
                    }
                },
                {
                    "teamId": 100,
                    "spell1Id": 6,
                    "spell2Id": 4,
                    "championId": 38,
                    "profileIconId": 15,
                    "summonerName": "Filét Mignon",
                    "bot": false,
                    "summonerId": "ky7gM5H0f3TMjuWpJivY4JehQumWP9Ks_uP4nfZRclpy7y0",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8128,
                            8143,
                            8138,
                            8135,
                            9111,
                            8014,
                            5008,
                            5008,
                            5002
                        ],
                        "perkStyle": 8100,
                        "perkSubStyle": 8000
                    }
                },
                {
                    "teamId": 100,
                    "spell1Id": 4,
                    "spell2Id": 21,
                    "championId": 31,
                    "profileIconId": 1152,
                    "summonerName": "Suppafly1234",
                    "bot": false,
                    "summonerId": "wUvagjkDiewYFwxLgQdC3jUbtWjZ1iU28D3fnrHROK3hAXQ",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8229,
                            8226,
                            8210,
                            8236,
                            8321,
                            8347,
                            5007,
                            5008,
                            5001
                        ],
                        "perkStyle": 8200,
                        "perkSubStyle": 8300
                    }
                },
                {
                    "teamId": 200,
                    "spell1Id": 4,
                    "spell2Id": 7,
                    "championId": 110,
                    "profileIconId": 1301,
                    "summonerName": "xxYxxF",
                    "bot": false,
                    "summonerId": "fTACPeutEW1UpmBgs3tojTuOHAeERfvLumuDwjb722xfPb8",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8229,
                            8226,
                            8210,
                            8236,
                            8138,
                            8105,
                            5008,
                            5008,
                            5001
                        ],
                        "perkStyle": 8200,
                        "perkSubStyle": 8100
                    }
                },
                {
                    "teamId": 200,
                    "spell1Id": 7,
                    "spell2Id": 4,
                    "championId": 32,
                    "profileIconId": 546,
                    "summonerName": "hispicychicken",
                    "bot": false,
                    "summonerId": "hiQyeTKWGA3-A3lZ0JeIbozXiHuOB3Riyv-JMW6Kdb1i5Iw",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8229,
                            8226,
                            8210,
                            8236,
                            8138,
                            8105,
                            5008,
                            5008,
                            5001
                        ],
                        "perkStyle": 8200,
                        "perkSubStyle": 8100
                    }
                },
                {
                    "teamId": 200,
                    "spell1Id": 6,
                    "spell2Id": 4,
                    "championId": 39,
                    "profileIconId": 654,
                    "summonerName": "beautychaostruth",
                    "bot": false,
                    "summonerId": "YxSG17nGGeqnsiBbZM5U1OpOKkc-OD7dmlrFeUO8KBBBF64",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8005,
                            9111,
                            9104,
                            8014,
                            8233,
                            8236,
                            5005,
                            5008,
                            5001
                        ],
                        "perkStyle": 8000,
                        "perkSubStyle": 8200
                    }
                },
                {
                    "teamId": 200,
                    "spell1Id": 4,
                    "spell2Id": 6,
                    "championId": 27,
                    "profileIconId": 3496,
                    "summonerName": "ChickenGaz25",
                    "bot": false,
                    "summonerId": "GAxkzWeaKyoHrpWnjeKCCDSjYNo-dKQWqJXVBP1eLphY70w",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8010,
                            9111,
                            9104,
                            8014,
                            8233,
                            8236,
                            5005,
                            5008,
                            5002
                        ],
                        "perkStyle": 8000,
                        "perkSubStyle": 8200
                    }
                },
                {
                    "teamId": 200,
                    "spell1Id": 4,
                    "spell2Id": 6,
                    "championId": 80,
                    "profileIconId": 4755,
                    "summonerName": "Chicken Eight",
                    "bot": false,
                    "summonerId": "rDmj3m3E8sFZVlhvPvfoSsECSkPxQfrx3E0eanhJG07VnvJH",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8128,
                            8126,
                            8138,
                            8135,
                            9111,
                            8014,
                            5008,
                            5008,
                            5002
                        ],
                        "perkStyle": 8100,
                        "perkSubStyle": 8000
                    }
                }
            ],
            "observers": {
                "encryptionKey": "w4IGI6PYURkJxSupl5bEBndM32uKf8gU"
            },
            "platformId": "NA1",
            "bannedChampions": [],
            "gameStartTime": 1654051429375,
            "gameLength": 443
        },
        {
            "gameId": 432786706789,
            "mapId": 11,
            "gameMode": "URF",
            "gameType": "MATCHED_GAME",
            "gameQueueConfigId": 900,
            "keySummoners": ["Snam", "grandtheftodom"],
            "participants": [
                {
                    "teamId": 100,
                    "isKey": true,
                    "spell1Id": 4,
                    "spell2Id": 14,
                    "championId": 105,
                    "profileIconId": 565,
                    "summonerName": "grandtheftodom",
                    "bot": false,
                    "summonerId": "Eny6Z_rz7V4oYwL1cHQFxvqqJhyyaAWyhYNM--4NWAPPQcA",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8128,
                            8143,
                            8138,
                            8105,
                            8014,
                            9111,
                            5008,
                            5008,
                            5002
                        ],
                        "perkStyle": 8100,
                        "perkSubStyle": 8000
                    }
                },
                {
                    "teamId": 100,
                    "isKey": true,
                    "spell1Id": 4,
                    "spell2Id": 6,
                    "championId": 6,
                    "profileIconId": 23,
                    "summonerName": "Snam",
                    "bot": false,
                    "summonerId": "lxCOZHPlnR-2MyoESLs99iFLV_5PMdFT-K1AbnTgRyHvO_0",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8005,
                            9111,
                            9104,
                            8014,
                            8139,
                            8135,
                            5005,
                            5008,
                            5002
                        ],
                        "perkStyle": 8000,
                        "perkSubStyle": 8100
                    }
                },
                {
                    "teamId": 100,
                    "spell1Id": 4,
                    "spell2Id": 7,
                    "championId": 16,
                    "profileIconId": 4022,
                    "summonerName": "Miyak",
                    "bot": false,
                    "summonerId": "7fshguUlCiCBrSHlUOkYEJDhwYGL6A4XvFeAsRIlMbtpdCI",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8214,
                            8224,
                            8210,
                            8237,
                            8473,
                            8453,
                            5008,
                            5008,
                            5002
                        ],
                        "perkStyle": 8200,
                        "perkSubStyle": 8400
                    }
                },
                {
                    "teamId": 100,
                    "spell1Id": 6,
                    "spell2Id": 4,
                    "championId": 38,
                    "profileIconId": 15,
                    "summonerName": "Filét Mignon",
                    "bot": false,
                    "summonerId": "ky7gM5H0f3TMjuWpJivY4JehQumWP9Ks_uP4nfZRclpy7y0",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8128,
                            8143,
                            8138,
                            8135,
                            9111,
                            8014,
                            5008,
                            5008,
                            5002
                        ],
                        "perkStyle": 8100,
                        "perkSubStyle": 8000
                    }
                },
                {
                    "teamId": 100,
                    "spell1Id": 4,
                    "spell2Id": 21,
                    "championId": 31,
                    "profileIconId": 1152,
                    "summonerName": "Suppafly1234",
                    "bot": false,
                    "summonerId": "wUvagjkDiewYFwxLgQdC3jUbtWjZ1iU28D3fnrHROK3hAXQ",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8229,
                            8226,
                            8210,
                            8236,
                            8321,
                            8347,
                            5007,
                            5008,
                            5001
                        ],
                        "perkStyle": 8200,
                        "perkSubStyle": 8300
                    }
                },
                {
                    "teamId": 200,
                    "spell1Id": 4,
                    "spell2Id": 7,
                    "championId": 110,
                    "profileIconId": 1301,
                    "summonerName": "xxYxxF",
                    "bot": false,
                    "summonerId": "fTACPeutEW1UpmBgs3tojTuOHAeERfvLumuDwjb722xfPb8",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8229,
                            8226,
                            8210,
                            8236,
                            8138,
                            8105,
                            5008,
                            5008,
                            5001
                        ],
                        "perkStyle": 8200,
                        "perkSubStyle": 8100
                    }
                },
                {
                    "teamId": 200,
                    "spell1Id": 7,
                    "spell2Id": 4,
                    "championId": 32,
                    "profileIconId": 546,
                    "summonerName": "hispicychicken",
                    "bot": false,
                    "summonerId": "hiQyeTKWGA3-A3lZ0JeIbozXiHuOB3Riyv-JMW6Kdb1i5Iw",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8229,
                            8226,
                            8210,
                            8236,
                            8138,
                            8105,
                            5008,
                            5008,
                            5001
                        ],
                        "perkStyle": 8200,
                        "perkSubStyle": 8100
                    }
                },
                {
                    "teamId": 200,
                    "spell1Id": 6,
                    "spell2Id": 4,
                    "championId": 39,
                    "profileIconId": 654,
                    "summonerName": "beautychaostruth",
                    "bot": false,
                    "summonerId": "YxSG17nGGeqnsiBbZM5U1OpOKkc-OD7dmlrFeUO8KBBBF64",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8005,
                            9111,
                            9104,
                            8014,
                            8233,
                            8236,
                            5005,
                            5008,
                            5001
                        ],
                        "perkStyle": 8000,
                        "perkSubStyle": 8200
                    }
                },
                {
                    "teamId": 200,
                    "spell1Id": 4,
                    "spell2Id": 6,
                    "championId": 27,
                    "profileIconId": 3496,
                    "summonerName": "ChickenGaz25",
                    "bot": false,
                    "summonerId": "GAxkzWeaKyoHrpWnjeKCCDSjYNo-dKQWqJXVBP1eLphY70w",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8010,
                            9111,
                            9104,
                            8014,
                            8233,
                            8236,
                            5005,
                            5008,
                            5002
                        ],
                        "perkStyle": 8000,
                        "perkSubStyle": 8200
                    }
                },
                {
                    "teamId": 200,
                    "spell1Id": 4,
                    "spell2Id": 6,
                    "championId": 80,
                    "profileIconId": 4755,
                    "summonerName": "Chicken Eight",
                    "bot": false,
                    "summonerId": "rDmj3m3E8sFZVlhvPvfoSsECSkPxQfrx3E0eanhJG07VnvJH",
                    "gameCustomizationObjects": [],
                    "perks": {
                        "perkIds": [
                            8128,
                            8126,
                            8138,
                            8135,
                            9111,
                            8014,
                            5008,
                            5008,
                            5002
                        ],
                        "perkStyle": 8100,
                        "perkSubStyle": 8000
                    }
                }
            ],
            "observers": {
                "encryptionKey": "w4IGI6PYURkJxSupl5bEBndM32uKf8gU"
            },
            "platformId": "NA1",
            "bannedChampions": [],
            "gameStartTime": 1654051429375,
            "gameLength": 443
        }
      ];