"use client"

import { AreaChart } from "@/components/AreaChart"
import {fetchIps, fetchRequests } from "@/api/ip"
import { groupByHour } from "@/lib/helpers"
import Map from "@/components/Map"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRoot,
  TableRow,
} from "@/components/Table"

interface IpData {
    [ip: string]: {
    dominio: string,
    estado: string,
    fecha_ult_reporte: string,
    pais: string,
    reportes_totales: number
    }
}

let response = await fetchIps()
const ipsData : IpData = response.data
response = await fetchRequests()
const requests = response.data

const byHour = groupByHour(requests)

const sortedByHour = Object.entries(byHour)
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

const RequestsChart = () => {
  const types: Array<"default" | "stacked" | "percent"> = [
    "default",
    "stacked",
    "percent",
  ]

  return (
        <div className="flex flex-col gap-16">
            <h2 className="text-3xl">Solicitudes por hora</h2>
            <div className="flex flex-col gap-4">
              <AreaChart
                key={0}
                type={types[0]}
                className="h-72"
                data={sortedByHour}
                index="hour"
                categories={["requests"]}
                showLegend={false}
              />
            </div>
            <h2 className="text-3xl">IPs detectadas</h2>
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
                  {Object.entries(ipsData).map(([ip, values]) => (
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
                      >{values.estado}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableRoot>
        </div>
        <Map ipData={ipsData} requestData={requests} />
    </div>
  )
}

export default RequestsChart
