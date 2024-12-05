import axios from "./axios"

export const getIpsData = async () => {
    const response = await axios.get('/get_data')
    return response.data
}

export const getIpData = async (ip: string) => {
    const response = await axios.get('get_ip_data?ip=' + ip)
    return response.data
}

export const fetchIps = async () => {
    const response = await axios.get('/fetch_data_from_db')
    return response.data
}

export const fetchRequests = async () => {
    const response = await axios.get('/fetch_requests_from_db')
    return response.data
}

export const getIpRequests = async (ip: string) => {
    const response = await axios.get('/get_ip_requests?ip=' + ip)
    return response.data
}

export const updateIps = async () => {
    const response = await axios.get('/update_ips')
    return response.data
}

export const connectKafka = async () => {
    const response = await axios.get('/connect_to_kafka')
    return response.data
}
