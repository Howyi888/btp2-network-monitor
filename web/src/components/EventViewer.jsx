import { ArrowForwardIcon } from "@chakra-ui/icons";
import { Badge, Box, Divider, Table, Tbody, Td, Text, Th, Thead, Tr } from "@chakra-ui/react";
import React, { useEffect, useRef, useState } from "react";
import { strfdelta } from "../utils";

interface Log {
    sn: Number;
    src: String;
    dst: String;
}

const COLOR_FOR = {
    good: 'green',
    bad: 'red'
}


function linkInfoForLog(log: Log) {
    return (
        <Text>{log.src_name}<ArrowForwardIcon />{log.dst_name}</Text>
    );
}

const rowForLog = (log: Log) => {
    const ts = new Date(log.ts*1000);
    let link = <Td></Td>;
    let msg = <Td></Td>;
    const extra = JSON.parse(log.extra);
    if (log.event === 'tx') {
        link = <Td>{linkInfoForLog(log)}</Td>
        msg = <Td><Text>count={extra.count}</Text></Td>
    } else if (log.event === 'rx') {
        link = <Td>{linkInfoForLog(log)}</Td>
        msg = <Td><Text>count={extra.count} delay={strfdelta(extra.delta)}</Text></Td>
    } else if (log.event === 'state') {
        link = <Td>{linkInfoForLog(log)}</Td>
        msg = <Td><Badge size='sm' colorScheme={COLOR_FOR[extra.after]}>{extra.after.toUpperCase()}</Badge></Td>
    } else {
        link = null
        msg = <Td colSpan='2'>{String(extra)}</Td>
    }
    return (
        <Tr id={log.sn} key={log.sn}>
            <Td isNumeric fontSize="xs">{log.sn}</Td>
            <Td>{ts.toLocaleString()}</Td>
            <Td>{log.event.toUpperCase()}</Td>
            {link}{msg}
        </Tr>
    )
}

const EventViewer = ({url}) => {
    const [events, setEvents] = useState([])
    const [start, setStart] = useState(null);
    const timer = useRef(null);
    const lastLine = useRef(null);
    const topLine = useRef(null);

    const requestUpdate = (timeout) => {
        if (timer.current) {
            clearTimeout(timer.current);
        }
        timer.current = setTimeout(updateEvents, timeout)
    }

    const loadEvents = async (params: String[]) => {
        const res = await fetch(url+'/events'+(params.length>0?'?'+params.join('&'):''));
        const data: Log[] = await res.json();
        return data;
    }

    const updateEvents = () => {
        if (events.length===0) {
            loadEvents([]).then((data) => {
                if (data.length > 0) {
                    setEvents(data.reverse());
                    setStart(data[0].sn);
                }
                requestUpdate(10000);
            }).catch(() => {
                requestUpdate(10000);
            });
        } else if (start < events[0].sn) {
            let params = [];
            params.push('before='+events[0].sn);
            let limit = events[0].sn - start;
            limit = limit > 100 ? 100 : limit;
            params.push('limit='+limit)
            loadEvents(params).then((data) => {
                if (data.length > 0) {
                    data.reverse();
                    events.forEach(event => {
                        data.push(event);
                    });
                    setEvents(data);
                    topLine.current.scrollIntoView({behavior: 'smooth'});
                } else {
                    setStart(events[0].sn);
                    requestUpdate(10000);
                }
            }).catch(()=> {
                requestUpdate(10000);
            });
        } else {
            let params = [];
            params.push('after='+(events[events.length-1].sn));
            loadEvents(params).then((data) => {
                if (data.length > 0) {
                    // console.log("Append:",data);
                    const new_data = events.concat(data);
                    setEvents(new_data);
                    lastLine.current.scrollIntoView({behavior: 'smooth'});
                } else {
                    requestUpdate(10000);
                }
            }).catch(()=>{
                requestUpdate(10000);
            });
        }
    }

    useEffect(() => {
        requestUpdate(200);
    }, [events, start]);

    return (
        <Box border="1px" flex="1" margin="6px" borderRadius="6px" borderColor="gray.400" overflowY="auto">
        <Table size="sm">
        <Thead position="sticky" top="0"><Tr ref={topLine} bg="gray.200">
            <Th width="5em">SN</Th>
            <Th width="20em">Time</Th>
            <Th width="5em">Event</Th>
            <Th width="20em">Link</Th>
            <Th>Extra</Th>
        </Tr></Thead>
        <Tbody>
        { start > 1 &&
            <Tr><Td colSpan="5" textAlign="center" padding="0px">
                <Text onClick={()=>{setStart(start>100 ? start-100 : 1)}} fontSize="7px">...LOAD PREVIOUS...</Text>
            </Td></Tr>
        }
        {events.map((item: Log) => rowForLog(item))}
        <Tr><Td colSpan="5" ref={lastLine} textAlign="center" padding="0px"><Divider /></Td></Tr>
        </Tbody>
        </Table>
        </Box>
    )
}

export default EventViewer