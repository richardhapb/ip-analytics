import React, { useEffect, useState } from 'react';
import { IpData, Requests } from '../types/models';
import { getCountryInfo } from '../api/countries';
import Worldmap from "../components/assets/Worldmap"

interface CountryRequestData {
  country: string;
  requests: number;
  name: string;
  latitude: number;
  longitude: number;
}

const WorldMap: React.FC<{
  ipData: IpData;
  requestData: Requests;
}> = ({ ipData, requestData }) => {
    const [countryRequests, setCountryRequests] = useState<CountryRequestData[]>([]);
    const [tooltip, setTooltip] = useState<{
        visible: boolean;
        content: string;
        x: number;
        y: number;
      }>({
        visible: false,
        content: '',
        x: 0,
        y: 0,
      });

const calculateRequestsPerCountry = (ipData: IpData, requestData: Requests): Record<string, number> => {
  const countryRequestCount: Record<string, number> = {};

  Object.keys(ipData).forEach((ip) => {
    const { pais } = ipData[ip]; 
    const requests = requestData[ip] || [];

    if (requests && Array.isArray(requests)) {

      if (!countryRequestCount[pais]) {
        countryRequestCount[pais] = 0;
      }
      countryRequestCount[pais] += requests.length;
    } else {
      console.log(`No se encontraron datos de requests para la IP: ${ip}`);
    }
  });

  return countryRequestCount;
};

  const fetchCountryDetails = async (countryCode: string): Promise<CountryRequestData | null> => {
    try {
      const countryInfo = await getCountryInfo(countryCode); 
      return {
        country: countryCode,
        requests: 0, 
        name: countryInfo.name,
        latitude: countryInfo.latitude,
        longitude: countryInfo.longitude,
      };
    } catch (error) {
      console.error(`Error obteniendo información para el país ${countryCode}:`, error);
      return null;
    }
  };

  useEffect(() => {
    const fetchAllCountryDetails = async () => {
      const countryRequestCount = calculateRequestsPerCountry(ipData, requestData);

      const countryRequestDetails = await Promise.all(
        Object.keys(countryRequestCount).map(async (country) => {
          const countryDetails = await fetchCountryDetails(country);
          if (countryDetails) {
            const totalRequests = countryRequestCount[country];
            countryDetails.requests = totalRequests; 
            return countryDetails;
          }
          return null;
        })
      );

      const validCountryRequests = countryRequestDetails.filter((item) => item !== null) as CountryRequestData[];
      setCountryRequests(validCountryRequests);
    };

    fetchAllCountryDetails();
  }, [ipData, requestData]);


useEffect(() =>  {
    // Update country colors by requests count
    if (countryRequests.length === 0) {
        return
    }

    countryRequests.map((country) => {
      const countryPaths = document.getElementsByClassName(country.name);

      if (countryPaths.length > 0) {
        const intensity = Math.min(Math.max(country.requests % 250, 50), 250);
        const redValue = 255 - Math.round((intensity / 250) * 155);
        const fillColor = `rgb(${redValue}, 30, 30)`;

        for (const element of countryPaths) {
          const el = element as SVGElement;

          el.setAttribute('fill', fillColor);

          // Tooltip events
          el.addEventListener('mouseenter', () => {
            setTooltip({
              visible: true,
              content: `${country.name}: ${country.requests} requests`,
              x: 0,
              y: 0,
            });
          });

          el.addEventListener('mousemove', (event) => {
            setTooltip((prev) => ({
              ...prev,
              x: event.pageX,
              y: event.pageY,
            }));
          });

          el.addEventListener('mouseleave', () => {
            setTooltip((prev) => ({ ...prev, visible: false }));
          });
        }
      }
    });
  }, [countryRequests]);

  return (
    <div className=''>
        <div className='w-2/3 mx-auto'>
            <Worldmap />

        </div>
    {tooltip.visible && (
            <div
              className="absolute bg-black text-white p-2 rounded"
              style={{ top: tooltip.y + 10, left: tooltip.x + 10 }}
            >
              {tooltip.content}
            </div>
          )}
        </div>
  );
};

export default WorldMap;
