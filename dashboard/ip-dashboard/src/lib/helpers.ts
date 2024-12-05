
type LogEntry = [number, string]; // [timestamp, path]
type LogsByIP = { [ip: string]: LogEntry[] };
type HourlySummary = { hour: string; requests: number }[];
type DailySummary = { day: string; requests: number }[];


export const groupByHour = (data: LogsByIP): HourlySummary => {
  const tempResult: { [hour: string]: number } = {};

  for (const ip in data) {
    const entries = data[ip];

    entries.forEach(([timestamp]) => {
      const hour = new Date(timestamp * 1000).toISOString().slice(0, 13); // YYYY-MM-DDTHH

      tempResult[hour] = (tempResult[hour] || 0) + 1;
    });
  }

  const result: HourlySummary = Object.entries(tempResult).map(([hour, requests]) => ({
    hour,
    requests,
  }));

  return result;
};

export const groupByDay = (data: LogsByIP): DailySummary => {
  const tempResult: { [day: string]: number } = {};

  for (const ip in data) {
    const entries = data[ip];

    entries.forEach(([timestamp]) => {
      const day = new Date(timestamp * 1000).toISOString().split("T")[0]; // YYYY-MM-DD

      tempResult[day] = (tempResult[day] || 0) + 1;
    });
  }

  const result: DailySummary = Object.entries(tempResult).map(([day, requests]) => ({
    day,
    requests,
  }));

  return result;
};
