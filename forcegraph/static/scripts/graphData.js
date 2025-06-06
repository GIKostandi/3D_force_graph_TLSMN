export function extractValue(valueObj) {
  if (!valueObj) return null;
  switch (valueObj.__typename) {
    case "StringValue":
      return valueObj.stringValue;
    case "StringLocaleValue":
      return valueObj.stringLocaleValue;
    case "IntValue":
      return valueObj.intValue;
    case "DoubleValue":
      return valueObj.floatValue;
    case "TimestampValue":
      return valueObj.timestampValue;
    case "LinkValue":
      return valueObj.linkValue?.name || valueObj.linkValue?.id;
    case "GeoPointValue":
      return {
        name: valueObj.name,
        point: valueObj.point,
      };
    case "DateTimeValue":
      return {
        date: valueObj.date,
        time: valueObj.time,
      };
    default:
      return null;
  }
}

export function buildGraphData(graphDataRaw) {
  if (!graphDataRaw?.data?.researchMap?.paginationConcept?.listConcept) {
    throw new Error("Некорректный JSON");
  }

  const nodes = new Map();
  const links = [];
  const validNodeIds = new Set();
  const conceptInfoMap = new Map();

  graphDataRaw.data.researchMap.paginationConcept.listConcept.forEach((concept) => {
    const conceptId = concept.id;
    const conceptName = concept.name;
    const conceptImage = concept.image;
    const conceptTypeId = concept.conceptType?.id;
    const conceptTypeName = concept.conceptType?.name;

    validNodeIds.add(conceptId);
    conceptInfoMap.set(conceptId, concept);

    const properties = {};
    if (concept.paginationConceptProperty) {
      concept.paginationConceptProperty.listConceptProperty.forEach((prop) => {
        const propName = prop.propertyType?.name;
        const propValueRaw = prop.value;

        let value;
        if (propValueRaw?.__typename === "CompositeValue" && propValueRaw.listValue) {
          value = propValueRaw.listValue.map((v) => extractValue(v.value));
        } else {
          value = extractValue(propValueRaw);
        }

        if (propName) {
          if (!properties[propName]) properties[propName] = [];

          if (Array.isArray(value)) {
            properties[propName].push(...value);
          } else {
            properties[propName].push(value);
          }
        }
      });
    }

    nodes.set(conceptId, {
      id: conceptId,
      name: conceptName,
      image: conceptImage,
      group: conceptTypeId,
      TypeName: conceptTypeName,
      properties,
    });
  });

  const linkSet = new Set();

  graphDataRaw.data.researchMap.paginationConcept.listConcept.forEach((concept) => {
    if (concept.paginationConceptLink) {
      concept.paginationConceptLink.listConceptLink.forEach((link) => {
        const fromId = link.from.id;
        const toId = link.to.id;
        const linkType = link.conceptLinkType.name;

        if (validNodeIds.has(fromId) && validNodeIds.has(toId)) {
          const key = `${fromId}->${toId}|${linkType}`;
          if (!linkSet.has(key)) {
            linkSet.add(key);
            links.push({
              source: fromId,
              target: toId,
              value: 1,
              label: linkType,
            });
          }
        }
      });
    }
  });

  const groupedLinks = new Map();
  links.forEach((link) => {
    const key = `${link.source}-${link.target}`;
    if (!groupedLinks.has(key)) groupedLinks.set(key, []);
    groupedLinks.get(key).push(link);
  });

  groupedLinks.forEach((linkGroup) => {
    const total = linkGroup.length;
    linkGroup.forEach((link, index) => {
      if (total === 1) {
        link.curvature = 0;
      } else {
        const offset = (index - (total - 1) / 2) * 0.3;
        link.curvature = offset;
      }
    });
  });

  const graphData = {
    nodes: Array.from(nodes.values()),
    links,
  };

  graphData.links.forEach((link) => {
    const a = graphData.nodes.find((n) => n.id === link.source);
    const b = graphData.nodes.find((n) => n.id === link.target);
    if (!a.neighbors) a.neighbors = [];
    if (!b.neighbors) b.neighbors = [];
    if (!a.links) a.links = [];
    if (!b.links) b.links = [];
    a.neighbors.push(b);
    b.neighbors.push(a);
    a.links.push(link);
    b.links.push(link);
  });

  return graphData;
}
