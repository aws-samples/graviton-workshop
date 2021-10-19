-- Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
-- Script for performance testing endpoints of an API


req0 = function()
    return wrk.format("GET", "/books")
end

req1 = function()
    return wrk.format("GET", "/books/1")
end

req2 = function()
    return wrk.format("GET", "/books/2")
end

req3 = function()
    return wrk.format("GET", "/carts/1")
end

req4 = function()
    return wrk.format("GET", "/carts/2/items")
end

requests = {}
requests[0] = req0
requests[1] = req1
requests[2] = req2
requests[3] = req3
requests[4] = req4

request = function()
    return requests[math.random(0, 4)]()
end

function fsize (file)
    local current = file:seek()      -- get current position
    local size = file:seek("end")    -- get file size
    file:seek("set", current)        -- restore position
    return size
end

-- Write latency performance profiles to CSV
done = function(summary, latency, requests)
    -- open output file
    f = io.open("test-result.csv", "a+")

    local fSize = fsize(f)

    if fSize == 0 then
        f:write("Percentile,Value (ms),Requests Per Second\n")
    end

    local duration_in_sec = (summary["duration"] / 1000000)
    local rps = (summary["requests"] / duration_in_sec)
    local _rps = string.format("%.2f RPS", rps)

    for _, p in pairs({ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 99.9, 99.999, 100 }) do
        f:write(string.format("%f,%f,%s\n",
       p,
       -- Dived all values by 1000 to get to ms
       (latency:percentile(p) / 1000), -- percentile latency
       _rps
       )
    )
    end

    f:close()
end
