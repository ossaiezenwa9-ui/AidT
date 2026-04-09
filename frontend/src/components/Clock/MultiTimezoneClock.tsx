import React, { useEffect, useState } from 'react';

const timezones = [
  { name: 'UTC', offset: 0, abbreviation: 'UTC' },
  { name: 'London', offset: 1, abbreviation: 'BST' },
  { name: 'New York', offset: -4, abbreviation: 'EDT' },
  { name: 'Tokyo', offset: 9, abbreviation: 'JST' },
  { name: 'Sydney', offset: 10, abbreviation: 'AEDT' },
];

const MultiTimezoneClock = () => {
  const [times, setTimes] = useState({});

  const updateTimes = () => {
    const currentTime = new Date();

    const newTimes = timezones.reduce((acc, timezone) => {
      const localTime = new Date(currentTime.getTime() + timezone.offset * 60 * 60 * 1000);
      const formattedTime = localTime.toISOString().slice(11, 19);
      acc[timezone.name] = formattedTime + ' ' + timezone.abbreviation;
      return acc;
    }, {});

    setTimes(newTimes);
  };

  useEffect(() => {
    updateTimes();
    const interval = setInterval(updateTimes, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col space-y-4 p-4 border rounded-lg shadow">
      <h2 className="text-xl font-bold">Current Time in Different Time Zones</h2>
      {Object.entries(times).map(([zone, time]) => (
        <div key={zone} className="text-lg">
          <span className="font-semibold">{zone}:</span> {time}
        </div>
      ))}
      {/* Add visual indicators for market sessions here */}
      <div className="text-sm mt-2">Market Session Status: Add indicators as needed.</div>
    </div>
  );
};

export default MultiTimezoneClock;