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
export default function DocumentList(documents) {
  return (
    <table className={"documentsTable"}>
      <thead>
        <tr>
          <th>File Name</th>
          <th>Tags</th>
        </tr>
      </thead>
      <tbody>
      {documents.map(document => (
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
