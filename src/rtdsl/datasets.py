from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


RAYJOIN_SAMPLE_URLS = {
    "br_county": "https://raw.githubusercontent.com/pwrliang/RayJoin/main/test/dataset/br_county_clean_25_odyssey_final.txt",
    "br_soil": "https://raw.githubusercontent.com/pwrliang/RayJoin/main/test/dataset/br_soil_ascii_odyssey_final.txt",
    "br_overlay_answer": "https://raw.githubusercontent.com/pwrliang/RayJoin/main/test/dataset/br_countyXbr_soil_answer.txt",
}

RAYJOIN_PREPROCESSED_SHARE_URL = "https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA"

RAYJOIN_PUBLIC_SOURCE_URLS = {
    "USCounty_item": "https://www.arcgis.com/home/item.html?id=14c5450526a8430298b2fa74da12c2f4",
    "Zipcode_item": "https://www.arcgis.com/home/item.html?id=d6f7ee6129e241cc9b6f75978e47128b",
    "BlockGroup_item": "https://www.arcgis.com/home/item.html?id=1c924a53319a491ab43d5cb1d55d8561",
    "WaterBodies_item": "https://www.arcgis.com/home/item.html?id=48c77cbde9a0470fb371f8c8a8a7421a",
    "Lakes_and_Parks_page": "https://spatialhadoop.cs.umn.edu/datasets.html",
}


@dataclass(frozen=True)
class CdbPoint:
    x: float
    y: float


@dataclass(frozen=True)
class CdbChain:
    chain_id: int
    point_count: int
    first_point_id: int
    last_point_id: int
    left_face_id: int
    right_face_id: int
    points: tuple[CdbPoint, ...]


@dataclass(frozen=True)
class CdbDataset:
    name: str
    chains: tuple[CdbChain, ...]

    def face_ids(self) -> tuple[int, ...]:
        face_ids = set()
        for chain in self.chains:
            if chain.left_face_id != 0:
                face_ids.add(chain.left_face_id)
            if chain.right_face_id != 0:
                face_ids.add(chain.right_face_id)
        return tuple(sorted(face_ids))


@dataclass(frozen=True)
class RayJoinPublicAsset:
    asset_id: str
    title: str
    source_type: str
    source_url: str
    preferred_use: str
    current_status: str
    notes: str


@dataclass(frozen=True)
class RayJoinBoundedPlan:
    handle: str
    source_requirement: str
    bounded_runtime_target: str
    deterministic_rule: str
    current_status: str
    notes: str


@dataclass(frozen=True)
class RayJoinFeatureServiceLayer:
    asset_id: str
    title: str
    source_url: str
    service_url: str
    layer_id: int
    geometry_type: str
    max_record_count: int
    feature_count: int
    current_status: str
    notes: str


RAYJOIN_PUBLIC_ASSETS: tuple[RayJoinPublicAsset, ...] = (
    RayJoinPublicAsset(
        asset_id="rayjoin_preprocessed_share",
        title="RayJoin preprocessed datasets share",
        source_type="dryad-share",
        source_url=RAYJOIN_PREPROCESSED_SHARE_URL,
        preferred_use="Preferred exact-input source for all paper dataset families when accessible.",
        current_status="source-identified",
        notes="RayJoin README states this share contains preprocessed datasets without exposing author identification.",
    ),
    RayJoinPublicAsset(
        asset_id="uscounty_arcgis",
        title="USA Census Counties",
        source_type="arcgis-item",
        source_url=RAYJOIN_PUBLIC_SOURCE_URLS["USCounty_item"],
        preferred_use="Exact-input source family for County ⊲⊳ Zipcode when using raw public data.",
        current_status="source-identified",
        notes="ArcGIS item currently resolves to an Esri Feature Service and is updated annually.",
    ),
    RayJoinPublicAsset(
        asset_id="zipcode_arcgis",
        title="USA ZIP Code Boundaries",
        source_type="arcgis-item",
        source_url=RAYJOIN_PUBLIC_SOURCE_URLS["Zipcode_item"],
        preferred_use="Exact-input source family for County ⊲⊳ Zipcode when using raw public data.",
        current_status="source-identified",
        notes="ArcGIS item currently resolves to an Esri Feature Service and is updated annually.",
    ),
    RayJoinPublicAsset(
        asset_id="blockgroup_arcgis",
        title="USA Census Block Group Boundaries",
        source_type="arcgis-item",
        source_url=RAYJOIN_PUBLIC_SOURCE_URLS["BlockGroup_item"],
        preferred_use="Exact-input source family for Block ⊲⊳ Water when using raw public data.",
        current_status="source-identified",
        notes="ArcGIS item is currently a retired Layer Package listing; manual export/conversion remains required.",
    ),
    RayJoinPublicAsset(
        asset_id="waterbodies_arcgis",
        title="USA Detailed Water Bodies",
        source_type="arcgis-item",
        source_url=RAYJOIN_PUBLIC_SOURCE_URLS["WaterBodies_item"],
        preferred_use="Exact-input source family for Block ⊲⊳ Water when using raw public data.",
        current_status="source-identified",
        notes="ArcGIS item currently resolves to an Esri Feature Service and also links to a layer-package variant.",
    ),
    RayJoinPublicAsset(
        asset_id="lakes_parks_spatialhadoop",
        title="SpatialHadoop public dataset catalog",
        source_type="dataset-catalog",
        source_url=RAYJOIN_PUBLIC_SOURCE_URLS["Lakes_and_Parks_page"],
        preferred_use="Derived-input source for continent-level Lakes/Parks pairs when exact-input share is unavailable.",
        current_status="source-identified",
        notes="The catalog lists public Lakes and Parks families; some historical Google Drive download links may no longer be live.",
    ),
)


RAYJOIN_BOUNDED_PLANS: tuple[RayJoinBoundedPlan, ...] = (
    RayJoinBoundedPlan(
        handle="USCounty__Zipcode",
        source_requirement="Need zipcode source acquisition plus conversion into RayJoin-compatible CDB before bounded County ⊲⊳ Zipcode runs.",
        bounded_runtime_target="5-10 minutes total package for the local comparison and reproduction loop.",
        deterministic_rule="Prefer exact-input Dryad share; otherwise derive a bounded CDB subset from raw USCounty + Zipcode with a fixed face/chain limit and stable sort by chain id.",
        current_status="source-identified",
        notes="County-side fixture exists now; zipcode-side local bounded subset does not.",
    ),
    RayJoinBoundedPlan(
        handle="USACensusBlockGroupBoundaries__USADetailedWaterBodies",
        source_requirement="Need both BlockGroup and WaterBodies acquisition plus conversion into RayJoin-compatible CDB before bounded Block ⊲⊳ Water runs.",
        bounded_runtime_target="5-10 minutes total package for the local comparison and reproduction loop.",
        deterministic_rule="Prefer exact-input Dryad share; otherwise derive bounded CDB subsets from raw BlockGroup + WaterBodies with fixed chain/face limits and stable sort by chain id.",
        current_status="source-identified",
        notes="No checked-in local subset currently exists for either family.",
    ),
    RayJoinBoundedPlan(
        handle="lakes_parks_continents",
        source_requirement="Need exact preprocessed continent pairs from Dryad or deterministic continent extraction from public Lakes/Parks sources before bounded LK* ⊲⊳ PK* runs.",
        bounded_runtime_target="5-10 minutes total package for Table 3 / Table 4 / Figure 15 analogue generation.",
        deterministic_rule="If exact-input share is unavailable, derive each continent pair deterministically from public Lakes/Parks sources and then apply a fixed chain-limit reduction per continent.",
        current_status="source-identified",
        notes="Goal 21 already froze the continent handle mapping from RayJoin scripts.",
    ),
)


RAYJOIN_FEATURE_SERVICE_LAYERS: tuple[RayJoinFeatureServiceLayer, ...] = (
    RayJoinFeatureServiceLayer(
        asset_id="uscounty_feature_layer",
        title="USA Census Counties Feature Layer",
        source_url=RAYJOIN_PUBLIC_SOURCE_URLS["USCounty_item"],
        service_url="https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_Counties/FeatureServer",
        layer_id=0,
        geometry_type="esriGeometryPolygon",
        max_record_count=2000,
        feature_count=3144,
        current_status="verified-live",
        notes="Verified via ArcGIS REST item metadata and layer query on 2026-04-02.",
    ),
    RayJoinFeatureServiceLayer(
        asset_id="zipcode_feature_layer",
        title="USA ZIP Code Boundaries Feature Layer",
        source_url=RAYJOIN_PUBLIC_SOURCE_URLS["Zipcode_item"],
        service_url="https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_ZIP_Code_Areas_anaylsis/FeatureServer",
        layer_id=0,
        geometry_type="esriGeometryPolygon",
        max_record_count=2000,
        feature_count=32294,
        current_status="verified-live",
        notes="Verified via ArcGIS REST item metadata and layer query on 2026-04-02.",
    ),
    RayJoinFeatureServiceLayer(
        asset_id="waterbodies_feature_layer",
        title="USA Detailed Water Bodies Feature Layer",
        source_url=RAYJOIN_PUBLIC_SOURCE_URLS["WaterBodies_item"],
        service_url="https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Detailed_Water_Bodies/FeatureServer",
        layer_id=0,
        geometry_type="esriGeometryPolygon",
        max_record_count=1000,
        feature_count=463591,
        current_status="verified-live",
        notes="Verified via ArcGIS REST item metadata and layer query on 2026-04-02; too large for the first Linux exact-input slice.",
    ),
)


def download_rayjoin_sample(name: str, destination: str | Path) -> Path:
    url = RAYJOIN_SAMPLE_URLS.get(name)
    if url is None:
        raise ValueError(f"unknown RayJoin sample dataset: {name}")

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(urlopen(url, timeout=30).read())
    return destination


def rayjoin_public_assets() -> tuple[RayJoinPublicAsset, ...]:
    return RAYJOIN_PUBLIC_ASSETS


def rayjoin_bounded_plans() -> tuple[RayJoinBoundedPlan, ...]:
    return RAYJOIN_BOUNDED_PLANS


def rayjoin_feature_service_layers() -> tuple[RayJoinFeatureServiceLayer, ...]:
    return RAYJOIN_FEATURE_SERVICE_LAYERS


def build_arcgis_layer_url(service_url: str, layer_id: int) -> str:
    return f"{service_url.rstrip('/')}/{layer_id}"


def build_arcgis_query_url(
    service_url: str,
    layer_id: int,
    *,
    offset: int,
    record_count: int,
    response_format: str = "geojson",
    where: str = "1=1",
    order_by_fields: str = "OBJECTID",
    out_fields: str = "*",
    out_sr: int = 4326,
) -> str:
    layer_url = build_arcgis_layer_url(service_url, layer_id)
    query = urlencode(
        {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "true",
            "f": response_format,
            "resultOffset": offset,
            "resultRecordCount": record_count,
            "orderByFields": order_by_fields,
            "outSR": out_sr,
        }
    )
    return f"{layer_url}/query?{query}"


def build_arcgis_geojson_query_url(
    service_url: str,
    layer_id: int,
    *,
    offset: int,
    record_count: int,
    response_format: str = "geojson",
    where: str = "1=1",
    order_by_fields: str = "OBJECTID",
    out_fields: str = "*",
    out_sr: int = 4326,
) -> str:
    return build_arcgis_query_url(
        service_url,
        layer_id,
        offset=offset,
        record_count=record_count,
        response_format=response_format,
        where=where,
        order_by_fields=order_by_fields,
        out_fields=out_fields,
        out_sr=out_sr,
    )


def load_cdb(path: str | Path) -> CdbDataset:
    path = Path(path)
    return parse_cdb_text(path.read_text(encoding="utf-8"), name=path.stem)


def parse_cdb_text(text: str, *, name: str) -> CdbDataset:
    raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
    chains = []
    index = 0

    while index < len(raw_lines):
        header = raw_lines[index].split()
        if len(header) != 6:
            raise ValueError(f"invalid CDB header at line {index + 1}: {raw_lines[index]}")

        chain_id, point_count, first_point_id, last_point_id, left_face_id, right_face_id = (
            int(value) for value in header
        )
        index += 1

        points = []
        for _ in range(point_count):
            if index >= len(raw_lines):
                raise ValueError(f"unexpected EOF while reading chain {chain_id}")
            point_fields = raw_lines[index].split()
            if len(point_fields) != 2:
                raise ValueError(f"invalid CDB point at line {index + 1}: {raw_lines[index]}")
            points.append(CdbPoint(x=float(point_fields[0]), y=float(point_fields[1])))
            index += 1

        chains.append(
            CdbChain(
                chain_id=chain_id,
                point_count=point_count,
                first_point_id=first_point_id,
                last_point_id=last_point_id,
                left_face_id=left_face_id,
                right_face_id=right_face_id,
                points=tuple(points),
            )
        )

    return CdbDataset(name=name, chains=tuple(chains))


def write_cdb(dataset: CdbDataset, destination: str | Path) -> Path:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for chain in dataset.chains:
        lines.append(
            f"{chain.chain_id} {chain.point_count} {chain.first_point_id} {chain.last_point_id} "
            f"{chain.left_face_id} {chain.right_face_id}"
        )
        for point in chain.points:
            lines.append(f"{point.x:.10e} {point.y:.10e}")
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination


def slice_cdb_dataset(
    dataset: CdbDataset,
    *,
    max_chains: int | None = None,
    max_faces: int | None = None,
    name: str | None = None,
) -> CdbDataset:
    chains = list(dataset.chains)
    if max_chains is not None:
        chains = chains[:max_chains]
    if max_faces is not None:
        allowed_faces: set[int] = set()
        filtered: list[CdbChain] = []
        for chain in chains:
            face_candidates = {face for face in (chain.left_face_id, chain.right_face_id) if face != 0}
            proposed_faces = allowed_faces | face_candidates
            if len(proposed_faces) <= max_faces or not filtered:
                filtered.append(chain)
                allowed_faces = proposed_faces
        chains = filtered
    return CdbDataset(name=name or dataset.name, chains=tuple(chains))


def chains_to_segments(dataset: CdbDataset, *, limit_chains: int | None = None) -> tuple[dict[str, float | int], ...]:
    chains = dataset.chains if limit_chains is None else dataset.chains[:limit_chains]
    records = []
    next_id = 1
    for chain in chains:
        for start, end in zip(chain.points, chain.points[1:]):
            records.append(
                {
                    "id": next_id,
                    "x0": start.x,
                    "y0": start.y,
                    "x1": end.x,
                    "y1": end.y,
                    "chain_id": chain.chain_id,
                }
            )
            next_id += 1
    return tuple(records)


def chains_to_probe_points(dataset: CdbDataset, *, limit_chains: int | None = None) -> tuple[dict[str, float | int], ...]:
    chains = dataset.chains if limit_chains is None else dataset.chains[:limit_chains]
    records = []
    for chain in chains:
        point = chain.points[0]
        records.append(
            {
                "id": chain.chain_id,
                "x": point.x,
                "y": point.y,
                "source_chain_id": chain.chain_id,
            }
        )
    return tuple(records)


def chains_to_polygon_refs(dataset: CdbDataset) -> tuple[dict[str, int], ...]:
    faces = {}
    for chain in dataset.chains:
        if chain.left_face_id != 0:
            faces.setdefault(chain.left_face_id, 0)
            faces[chain.left_face_id] += 1
        if chain.right_face_id != 0:
            faces.setdefault(chain.right_face_id, 0)
            faces[chain.right_face_id] += 1

    refs = []
    for index, face_id in enumerate(sorted(faces), start=0):
        refs.append({"id": face_id, "vertex_offset": index, "vertex_count": faces[face_id]})
    return tuple(refs)
