import ReactDOM from "react-dom";
import React, { useEffect, useState } from "react";
import { Container, Table } from "reactstrap";
import { useClient } from "./util/api";
import { SampleFilter } from "./trend/sampleFilter";

function ReportTable() {
  const [samples, setSamples] = useState([]);
  const [dataTypes, setDataTypes] = useState([]);
  const [client, user] = useClient();
  useEffect(() => {
    if (user) {
      client
        .find("samples", {
          "page[size]": 0,
          include: "data.data_type",
        })
        .then((samples) => {
          const newDataTypes = new Set();
          setSamples(
            samples.map((resource) => {
              const tree = resource.toJSONTree();
              // TODO: Fix data being null here
              if (tree.data) {
                for (const data of tree.data) {
                  newDataTypes.add(data.data_type.key);
                }
              }
              return tree;
            })
          );
          setDataTypes(Array.from(newDataTypes));
        });
    }
  }, [user]);
  return (
    <>
      <Container>
        <SampleFilter
          qcApi={client}
          onFilterChange={(filter) => {}}
          user={user}
        />
      </Container>
      <Container>
        <Table responsive={true}>
          <thead>
            <tr>
              {dataTypes.map((type) => (
                <th key={type}>{type}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {samples.map((sample) => (
              <tr key={sample.id}>
                {dataTypes.map((type) => {
                  const matched = sample.data.filter(
                    (data) => data.data_type.key == type
                  );
                  const data = matched.length === 0 ? "" : matched[0].value;
                  return <td key={`${sample.id}_${type}`}>{data}</td>;
                })}
              </tr>
            ))}
          </tbody>
        </Table>
      </Container>
    </>
  );
}

ReactDOM.render(<ReportTable />, document.getElementById("react"));
