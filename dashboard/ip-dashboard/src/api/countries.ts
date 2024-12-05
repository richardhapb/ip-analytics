import axios from "../api/axios"

const API_URL = "https://restcountries.com/v3.1/alpha"

export const getCountryInfo = async (countryCode: string) => {
    const response = await axios.get(API_URL + '/' + countryCode)
    const data = response.data[0]

    const name = data.name.common
    const [lat, lon] = data.latlng

    const info = {
        name: name,
        latitude: lat,
        longitude: lon
    }

    return info
    
}
