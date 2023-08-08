import { Badge, Box, Divider, HStack, IconButton, MenuItemOption, MenuOptionGroup, Table, Tbody, Td, Text, Th, Thead, Tr, Icon, Spinner } from "@chakra-ui/react";
import { Menu, MenuButton, MenuList, Flex } from "@chakra-ui/react";
import React, { useEffect, useRef, useState } from "react";
import { strfdelta } from "../utils";
import { TbFilter } from "react-icons/tb";
import { BiArrowToBottom, BiArrowToTop } from "react-icons/bi";

interface Log {
    sn: Number;
    src: String;
    dst: String;
    event: String;
    extra: String;
    src_name: String;
    dst_name: String;
}

const COLOR_FOR = {
    good: 'green',
    bad: 'red'
}

const TOP_LINE = 'top'
const LAST_LINE = 'last'


function linkInfoForLog(log: Log) {
    return (
        <>{log.src_name}→{log.dst_name}</>
    );
}

function connNameForLog(log: Log) {
    return log.src_name+"→︎"+log.dst_name;
}

function connIDForLog(log: Log) {
    if (log.src === null || log.dst === null) return null;
    if (log.src === undefined || log.dst === undefined) return null;
    if (log.src === '-' || log.dst === '-') return null;
    return log.src+":"+log.dst;
}

function filterLog(filter: String, log: Log): Boolean {
    if (filter==='none') return false;
    const id = connIDForLog(log)
    if (id===null) return false;
    return id !== filter;
}

const rowForLog = (filter: String, log: Log) => {
    const display = filterLog(filter, log) ? "none" : null;
    const ts = new Date(log.ts*1000);
    let message = null;
    const extra = JSON.parse(log.extra);
    if (log.event === 'tx') {
        message = <Td>
            {linkInfoForLog(log)} : &nbsp;
            <Badge size='sm' colorScheme="blue">TX</Badge>
            {extra.seq!==undefined && <> &bull; SEQ={extra.seq}</>}
            &nbsp;&bull; COUNT={extra.count}
        </Td>
    } else if (log.event === 'rx') {
        message = <Td>
            {linkInfoForLog(log)} : &nbsp;
            <Badge size='sm' colorScheme="blue">RX</Badge>
            {extra.seq!==undefined && <> &bull; SEQ={extra.seq}</>}
            &nbsp;&bull; COUNT={extra.count} &bull; DELAY={strfdelta(extra.delta)}
        </Td>
    } else if (log.event === 'state') {
        message = <Td>
            {linkInfoForLog(log)} : &nbsp;
            <Badge size='sm' colorScheme={COLOR_FOR[extra.after]}>
                {extra.after.toUpperCase()}
            </Badge>
        </Td>
    } else {
        message = <Td>{String(extra)}</Td>;
    }
    return (
        <Tr id={log.sn} key={log.sn} className={'row-'+log.event} display={display}>
            <Td isNumeric fontSize="xs">{log.sn}</Td>
            <Td>{ts.toLocaleString()}</Td>
            <Td>{log.event.toUpperCase()}</Td>
            {message}
        </Tr>
    )
}

const EventViewer = ({url}) => {
    const [events, setEvents] = useState([]);
    const [start, setStart] = useState(null);
    const [current, setCurrent] = useState(Date.now());
    const isLoading = useRef(false);
    const timer = useRef(null);
    const lastLine = useRef(null);
    const topLine = useRef(null);
    const range = useRef(null);
    const queryNames = useRef(null);
    const scrollTarget = useRef(null);
    const top = useRef(1);
    const [eventNames, setEventNames] = useState(['state', 'log', 'tx'])

    const requestUpdate = (timeout) => {
        if (timer.current) {
            clearTimeout(timer.current);
        }
        timer.current = setTimeout(() => {
            timer.current = null;
            setCurrent(Date.now());
        }, timeout)
    };

    const connections = useRef(new Map());
    const makeConnections = (logs) => {
        let conns = new Map();
        logs.forEach((log: Log) => {
            const connID = connIDForLog(log);
            if (connID !== null && !conns.has(connID)) {
                conns.set(connID, connNameForLog(log));
            }
        });
        return conns;
    };

    const loadEventsEx = async (uri: String, params: Map<String,String>) => {
        let url = uri+'/events'
        if (params.size !== 0) {
            let ps = [];
            params.forEach((value: String, key: String) => {
                ps.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
            });
            url += '?' + ps.join('&');
        }
        const res = await fetch(url);
        const data: Log[] = await res.json();
        return data;
    };

    useEffect(() => {
        if (isLoading.current) return;
        isLoading.current = true;
        if (String(queryNames.current) !== eventNames.toString()) {
            queryNames.current = eventNames;
            range.current = null;
            top.current = 1;
            setStart(null);
        }
        if (range.current === null) {
            let params = new Map();
            params.set("events", eventNames.join(","));
            loadEventsEx(url, params).then((data) => {
                if (data.length > 0) {
                    setEvents(data.reverse());
                    scrollTarget.current = LAST_LINE;
                } else {
                    requestUpdate(10000);
                }
            }).catch(() => {
                requestUpdate(10000);
            }).finally(() => {
                isLoading.current = false;
            });
        } else if (start !== null && start < range.current.first) {
            let params = new Map();
            params.set("events", eventNames.join(","));
            params.set('before', range.current.first);
            let limit = range.current.first - start;
            limit = limit > 100 ? 100 : limit;
            params.set('limit', limit)
            loadEventsEx(url, params).then((data) => {
                if (data.length > 0) {
                    data.reverse();
                    setEvents((events) => {
                        return data.concat(events);
                    })
                    scrollTarget.current = TOP_LINE;
                } else {
                    top.current = range.current.first;
                    setStart(range.current.first);
                    requestUpdate(10000);
                }
            }).catch(()=> {
                requestUpdate(10000);
            }).finally(() => {
                isLoading.current = false;
            });
        } else {
            let params = new Map();
            params.set("events", eventNames.join(","));
            params.set('after', range.current.last);
            loadEventsEx(url, params).then((data) => {
                if (data.length > 0) {
                    setEvents((events) => {
                        return events.concat(data)
                    });
                    scrollTarget.current = LAST_LINE;
                } else {
                    requestUpdate(10000);
                }
            }).catch(()=>{
                requestUpdate(10000);
            }).finally(() => {
                isLoading.current = false;
            });
        }
    }, [current, url, start, eventNames]);

    useEffect(() => {
        requestUpdate(200);
        if (events.length >0) {
            range.current = {
                first: events[0].sn,
                last: events[events.length-1].sn
            };
            connections.current = makeConnections(events);
        }
    }, [events]);

    const scrollTo = (to, behavior?) => {
        if (behavior === undefined) {
            behavior = 'instant';
        }
        if (to === TOP_LINE) {
            topLine.current.scrollIntoView({
                behavior: behavior,
                block: 'center',
            });
        }
        if (to === LAST_LINE) {
            lastLine.current.scrollIntoView({
                behavior: behavior,
                block: 'center',
            });
        }
    }

    useEffect(() => {
        if (scrollTarget.current!==null) {
            scrollTo(scrollTarget.current, 'smooth');
            scrollTarget.current = null;
        }
    });

    const EventSelector = ({children}) => {
        return <Menu>
            <MenuButton as={Flex} className="filter-selector">
                <HStack gap={0}>{children}</HStack>
            </MenuButton>
            <MenuList>
            <MenuOptionGroup type="checkbox" value={eventNames} onChange={setEventNames}>
            <MenuItemOption value="log">LOG</MenuItemOption>
            <MenuItemOption value="tx">TX/RX</MenuItemOption>
            <MenuItemOption value="state">STATE</MenuItemOption>
            </MenuOptionGroup>
            </MenuList>
        </Menu>
    }

    const [ messageFilter, setMessageFilter ] = useState("none");
    const MessageFilter = ({children}) => {
        return <Menu>
            <MenuButton as={Flex} className="filter-selector">
                <HStack gap={0}>{children}</HStack>
            </MenuButton>
            <MenuList>
                <MenuOptionGroup value={messageFilter} onChange={setMessageFilter}>
                    <MenuItemOption value="none">No Filter</MenuItemOption>
                    {Array.from(connections.current.keys()).sort().map((key) => {
                        const value = connections.current.get(key);
                        return <MenuItemOption value={key} key={key}>{value}</MenuItemOption>;
                    })}
                </MenuOptionGroup>
            </MenuList>
        </Menu>
    }

    return (
        <Box border="1px" flex="1" margin="6px" borderRadius="6px" borderColor="gray.400" overflowY="auto" className="event-viewer">
        <Table size="sm" className="event-log">
        <Thead position="sticky" top="0"><Tr bg="gray.200">
            <Th>SN</Th>
            <Th>Time</Th>
            <Th><EventSelector><Text>Event&bull;</Text><Icon as={TbFilter}/></EventSelector></Th>
            <Th>
            <HStack>
                <Flex flex="1">
                    <MessageFilter>
                        <Text>Messages&bull;</Text><Icon as={TbFilter} />
                        <Text>&bull;{connections.current.get(messageFilter) || "No Filter"}</Text>
                    </MessageFilter>
                </Flex>
                <Flex>
                    <IconButton size="sm" variant="link" onClick={()=>{scrollTo(TOP_LINE);}} icon={<Icon as={BiArrowToTop} />}></IconButton>
                    <IconButton size="sm" variant="link" onClick={()=>{scrollTo(LAST_LINE);}} icon={<Icon as={BiArrowToBottom} />}></IconButton>
                </Flex>
            </HStack>
            </Th>
        </Tr></Thead>
        <Tbody className="normal">
        <Tr><Td colSpan="5" ref={topLine} textAlign="center" padding="0px" className="top-line">
            { (start !== null) && (start<events[0].sn) ?
                <Text>...LOADING <Spinner size="xs" />...</Text>
                :
                <>
                { events.length > 0 && events[0].sn > top.current ?
                    <Text onClick={()=>{setStart(events[0].sn>100 ? events[0].sn-100 : 1)}}>...LOAD PREVIOUS...</Text>
                    :
                    <Divider />
                }
                </>
            }
        </Td></Tr>
        {events.map((item: Log) => rowForLog(messageFilter, item))}
        <Tr><Td colSpan="5" ref={lastLine} textAlign="center" padding="0px" className="bottom-line"><Divider /></Td></Tr>
        </Tbody>
        </Table>
        </Box>
    )
}

export default EventViewer