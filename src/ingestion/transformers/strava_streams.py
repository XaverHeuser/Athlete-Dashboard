from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from models.strava_stream_model import (
    StravaActivityStreamRow,
    StravaStreamsResponse,
)


def explode_streams(
    activity_id: int,
    raw_streams: dict[str, Any],
) -> list[StravaActivityStreamRow]:
    """
    Explodes Strava activity streams JSON into row-based Bronze records.
    """

    parsed = StravaStreamsResponse.model_validate(raw_streams)

    rows: list[StravaActivityStreamRow] = []
    loaded_at = datetime.now(timezone.utc)

    # ✅ Pydantic v2: .root
    for stream_type, stream in parsed.root.items():
        if not stream.data:
            continue

        for sequence_index, value in enumerate(stream.data):
            row_data: dict[str, Any] = {
                'activity_id': activity_id,
                'stream_type': stream_type,
                'sequence_index': sequence_index,
                'loaded_at': loaded_at,
            }

            if isinstance(value, bool):
                row_data['value_bool'] = value

            elif isinstance(value, int):
                row_data['value_int'] = value

            elif isinstance(value, float):
                row_data['value_float'] = value

            elif (
                stream_type == 'latlng'
                and isinstance(value, list)
                and len(value) == 2
                and all(isinstance(v, (int, float)) for v in value)
            ):
                row_data['value_lat'] = float(value[0])
                row_data['value_lng'] = float(value[1])

            else:
                continue

            rows.append(StravaActivityStreamRow(**row_data))

    return rows
