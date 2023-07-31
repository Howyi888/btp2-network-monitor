import { Badge, Box, Divider, HStack, IconButton, MenuItemOption, MenuOptionGroup, Table, Tbody, Td, Text, Th, Thead, Tr, Icon } from "@chakra-ui/react";
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
    const scrollTarget = useRef(null);

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
    }

    const loadEvents = async (url: String, params: String[]) => {
        const res = await fetch(url+'/events'+(params.length>0?'?'+params.join('&'):''));
        const data: Log[] = await res.json();
        return data;
    }

    useEffect(() => {
        if (isLoading.current) return;
        isLoading.current = true
        if (range.current === null) {
            loadEvents(url, []).then((data) => {
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
            let params = [];
            params.push('before='+range.current.first);
            let limit = range.current.first - start;
            limit = limit > 100 ? 100 : limit;
            params.push('limit='+limit)
            loadEvents(url, params).then((data) => {
                if (data.length > 0) {
                    data.reverse();
                    setEvents((events) => {
                        return data.concat(events);
                    })
                    scrollTarget.current = TOP_LINE;
                } else {
                    setStart(range.current.first);
                    requestUpdate(10000);
                }
            }).catch(()=> {
                requestUpdate(10000);
            }).finally(() => {
                isLoading.current = false;
            });
        } else {
            let params = [];
            params.push('after='+range.current.last);
            loadEvents(url, params).then((data) => {
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
    }, [current, url, start]);

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

    const [ bodyClass, setBodyClass ] = useState('normal');
    const [ showFlags, setShowFlags ] = useState(["log", "tx", "state"]);
    useEffect(() => {
        let classes = [];
        if (!showFlags.includes('log')) {
            classes.push('hide-log')
        }
        if (!showFlags.includes('tx')) {
            classes.push('hide-tx')
        }
        if (!showFlags.includes('state')) {
            classes.push('hide-state')
        }
        if (classes.length === 0) {
            setBodyClass('normal')
        } else {
            let className = "";
            classes.forEach((cls) => {
                className += " "+cls;
            })
            setBodyClass(className.substring(1));
        }
    }, [showFlags])

    const EventSelector = ({children}) => {
        return <Menu>
            <MenuButton as={Flex} className="filter-selector">
                <HStack gap={0}>{children}</HStack>
            </MenuButton>
            <MenuList>
            <MenuOptionGroup type="checkbox" value={showFlags} onChange={setShowFlags}>
            <MenuItemOption value="log">LOG</MenuItemOption>
            <MenuItemOption value="tx">TX</MenuItemOption>
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
        <Tbody className={bodyClass}>
        <Tr><Td colSpan="5" ref={topLine} textAlign="center" padding="0px" className="top-line">
            { events.length > 0 && events[0].sn > 1 ?
                <Text onClick={()=>{setStart(events[0].sn>100 ? events[0].sn-100 : 1)}}>...LOAD PREVIOUS...</Text>
                :
                <Divider />
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