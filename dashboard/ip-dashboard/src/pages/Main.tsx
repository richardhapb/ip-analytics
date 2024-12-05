"use client"

import { AreaChart } from "../components/AreaChart"
import { fetchRequests, updateIps, fetchIps } from "../api/ip"
import { groupByHour } from "../lib/helpers"
import Map from "../components/Map"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRoot,
  TableRow,
} from "../components/Table"
import { useState, useEffect } from "react"

import type { Requests } from "../types/models"

interface IpData {
  [ip: string]: {
    dominio: string,
    estado: string,
    fecha_ult_reporte: string,
    pais: string,
    reportes_totales: number
  }
}

const RequestsChart = () => {
  const [ipsData, setIpsData] = useState<IpData>({})
  const [requests, setRequests] = useState<any[]>([])
  const [sortedByHour, setSortedByHour] = useState<any[]>([])
  const [filter, setFilter] = useState("Todo")
  const [filteredIps, setFilteredIps] = useState<IpData>({})
  const [firstRequest, setFirstRequest] = useState(true)


  // Initial fetch and updating
  useEffect(() => {
    const fetchData = async () => {
      try {
        let ipsResponse = {data:{}}
        if (firstRequest){
           ipsResponse = await fetchIps()
           if(Object.keys(ipsResponse.data).length === 0) {
               ipsResponse = await updateIps()
           }
           setFilteredIps(ipsResponse.data)
           setFirstRequest(false)
        }
        else {
           ipsResponse = await updateIps()
        }
        const requestsResponse = await fetchRequests()

        const ips = ipsResponse.data
        const reqs = requestsResponse.data
        setIpsData(ips)
        setRequests(reqs)

        const byHour = groupByHour(reqs)
        const sorted = Object.entries(byHour)
          .sort((hourA, hourB) => {
            const [dateA, hour2A] = hourA[1].hour.split('T')
            const [dateB, hour2B] = hourB[1].hour.split('T')

            const hourAInt = parseInt(hour2A, 10)
            const hourBInt = parseInt(hour2B, 10)

            const dateComparasion = dateA.localeCompare(dateB)
            if (dateComparasion !== 0) {
              return dateComparasion
            }

            return hourAInt - hourBInt
          }).map(item => item[1])

        setSortedByHour(sorted)
      } catch (error) {
        console.error("Error fetching data:", error)
      }
    }

    // Get initial data and update each 10 seconds

    fetchData()

    const interval = setInterval(() => {
        fetchData()
    }, 10000)

    return () => clearInterval(interval)
  }, [])


  // Filter by status
  const handleFilterChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedFilter = event.target.value
    setFilter(selectedFilter)

    if (selectedFilter === "Todo") {
      setFilteredIps(ipsData) 
    } else {
      const filteredData = Object.fromEntries(
        Object.entries(ipsData).filter(([_, values]) => values.estado === selectedFilter)
      )
      setFilteredIps(filteredData) 
    }
  }

  return (
    <div className="flex flex-col gap-16">
      <h1 className="text-4xl my-0">Visualización de logs visitas página web</h1>
      <p className="text-xs text-gray italic">Todas las clasificaciones vienen determinadas por el número de reportes en página abuseipdb.com</p>
      {firstRequest && <h1 className="text-4xl text-center">Cargando datos...</h1> }
      <h2 className="text-3xl">Solicitudes por hora</h2>
      <div className="flex flex-col gap-4">
        <AreaChart
          key={0}
          type="default"
          className="h-72"
          data={sortedByHour}
          index="hour"
          categories={["requests"]}
          showLegend={false}
        />
      </div>
      <h2 className="text-3xl">IPs detectadas</h2>
      <div className="mb-4">
        <label htmlFor="filter" className="block text-lg mb-2">Filtrar por estado:</label>
        <select
          id="filter"
          value={filter}
          onChange={handleFilterChange}
          className="p-2 border border-gray-300 rounded text-black min-w-40"
        >
          <option value="Todo">Todo</option>
          <option value="Confiable">Confiable</option>
          <option value="Sospechosa">Sospechosa</option>
          <option value="Maliciosa">Maliciosa</option>
        </select>
      </div>
      <div className="overflow-auto max-h-96">
        <TableRoot>
          <Table>
            <TableCaption>IPs detectadas</TableCaption>
            <TableHead>
              <TableRow>
                <TableHeaderCell>IP</TableHeaderCell>
                <TableHeaderCell>Dominio</TableHeaderCell>
                <TableHeaderCell>País</TableHeaderCell>
                <TableHeaderCell>Último reporte</TableHeaderCell>
                <TableHeaderCell>Reportes totales</TableHeaderCell>
                <TableHeaderCell>Estado</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.entries(filteredIps).map(([ip, values]) => (
                <TableRow key={ip}>
                  <TableCell>{ip}</TableCell>
                  <TableCell>{values.dominio}</TableCell>
                  <TableCell>{values.pais}</TableCell>
                  <TableCell>{values.fecha_ult_reporte}</TableCell>
                  <TableCell>{values.reportes_totales}</TableCell>
                  <TableCell
                    className={
                      values.estado === "Maliciosa" ? "dark:text-red-500 font-bold" : ""
                    }
                  >
                    {values.estado}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableRoot>
      </div>
      <Map ipData={filteredIps} requestData={requests as unknown as Requests} />
    </div>
  )
}

export default RequestsChart
