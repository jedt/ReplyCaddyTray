import React, {useEffect, useState} from 'react';

import './DocumentList.css';
function displayTags(tags) {
  // for each tags
  return tags.map(tag => {
    return (
      <span className={"tagWrapper"} key={tag}>
        {tag}
      </span>
    );
  });
}
export default function DocumentList() {
  const [documents, setDocuments] = useState([]);
  useEffect(() => {
    fetch('http://127.0.0.1:8971/api/data')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => setDocuments(data))
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
      });
  }, []);

  return (
    <table className={"documentsTable"}>
      <thead>
        <tr>
          <th>File Name</th>
          <th>Tags</th>
        </tr>
      </thead>
      <tbody>
      {documents.slice(0, 4).map(document => (
        <tr className={"rowItem"} key={document.file_name}>
          <td>
            <span>{document.file_name}</span>
          </td>
          <td>
            {displayTags(document.tags)}
          </td>
        </tr>
      ))}
      </tbody>
    </table>
  );
};
