export interface IpData {
    [ip: string]: {
    dominio: string,
    estado: string,
    fecha_ult_reporte: string,
    pais: string,
    reportes_totales: number
    }
}

export interface Requests {
    [ip: string]: {
        Array:Array<[number, string]>
    }
}
