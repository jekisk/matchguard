using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

public class MatchGuardClient : MonoBehaviour
{
    [SerializeField] private string apiUrl = "https://example.com/analyze";
    [SerializeField] private string matchId = "local-match";
    [SerializeField] private string playerId = "local-player";

    private readonly List<string> pendingEvents = new();

    public void TrackMovement(Vector3 position)
    {
        pendingEvents.Add(JsonUtility.ToJson(new MovementEvent
        {
            match_id = matchId,
            player_id = playerId,
            type = "movement",
            ts = Time.time,
            position = new Position { x = position.x, y = position.y, z = position.z }
        }));
    }

    public void TrackShot(float yaw, float pitch, bool hit, bool headshot, bool targetVisible)
    {
        pendingEvents.Add(JsonUtility.ToJson(new ShotEvent
        {
            match_id = matchId,
            player_id = playerId,
            type = "shot",
            ts = Time.time,
            view_angle = new ViewAngle { yaw = yaw, pitch = pitch },
            hit = hit,
            headshot = headshot,
            target_visible = targetVisible
        }));
    }

    public IEnumerator Flush()
    {
        if (pendingEvents.Count == 0)
        {
            yield break;
        }

        string body = "{\"events\":[" + string.Join(",", pendingEvents) + "]}";
        pendingEvents.Clear();

        using UnityWebRequest request = new(apiUrl, "POST");
        byte[] payload = Encoding.UTF8.GetBytes(body);
        request.uploadHandler = new UploadHandlerRaw(payload);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogWarning("MatchGuard upload failed: " + request.error);
        }
    }

    [System.Serializable]
    private struct Position
    {
        public float x;
        public float y;
        public float z;
    }

    [System.Serializable]
    private struct ViewAngle
    {
        public float yaw;
        public float pitch;
    }

    [System.Serializable]
    private struct MovementEvent
    {
        public string match_id;
        public string player_id;
        public string type;
        public float ts;
        public Position position;
    }

    [System.Serializable]
    private struct ShotEvent
    {
        public string match_id;
        public string player_id;
        public string type;
        public float ts;
        public ViewAngle view_angle;
        public bool hit;
        public bool headshot;
        public bool target_visible;
    }
}
