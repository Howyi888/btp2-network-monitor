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
}

const COLOR_FOR = {
    good: 'green',
    bad: 'red'
}


function linkInfoForLog(log: Log) {
    return (
        <>{log.src_name}→{log.dst_name}</>
    );
}

const rowForLog = (log: Log) => {
    const ts = new Date(log.ts*1000);
    let message = null;
    const extra = JSON.parse(log.extra);
    if (log.event === 'tx') {
        message = <Td>
            {linkInfoForLog(log)} : &nbsp;
            <Badge size='sm' colorScheme="blue">TX</Badge> &bull;
            COUNT={extra.count}
        </Td>
    } else if (log.event === 'rx') {
        message = <Td>
            {linkInfoForLog(log)} : &nbsp;
            <Badge size='sm' colorScheme="blue">RX</Badge> &bull;
            COUNT={extra.count} DELAY={strfdelta(extra.delta)}
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
        <Tr id={log.sn} key={log.sn} className={'row-'+log.event}>
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

    const requestUpdate = (timeout) => {
        if (timer.current) {
            clearTimeout(timer.current);
        }
        timer.current = setTimeout(() => {
            timer.current = null;
            setCurrent(Date.now());
        }, timeout)
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
                    lastLine.current.scrollIntoView();
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
                    topLine.current.scrollIntoView({
                        block: 'end',
                        behavior: 'smooth'
                    });
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
                    })
                    lastLine.current.scrollIntoView({behavior: 'smooth'});
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
        }
    }, [events]);

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

    return (
        <Box border="1px" flex="1" margin="6px" borderRadius="6px" borderColor="gray.400" overflowY="auto" className="event-viewer">
        <Table size="sm" className="event-log">
        <Thead position="sticky" top="0"><Tr bg="gray.200">
            <Th>SN</Th>
            <Th>Time</Th>
            <Th><EventSelector><Text>Event&bull;</Text><Icon as={TbFilter}/></EventSelector></Th>
            <Th>
            <HStack>
                <Flex flex="1">Message</Flex>
                <Flex>
                    <IconButton size="sm" variant="link" onClick={()=>{topLine.current.scrollIntoView(false)}} icon={<Icon as={BiArrowToTop} />}></IconButton>
                    <IconButton size="sm" variant="link" onClick={()=>{lastLine.current.scrollIntoView()}} icon={<Icon as={BiArrowToBottom} />}></IconButton>
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
        {events.map((item: Log) => rowForLog(item))}
        <Tr><Td colSpan="5" ref={lastLine} textAlign="center" padding="0px" className="bottom-line"><Divider /></Td></Tr>
        </Tbody>
        </Table>
        </Box>
    )
}

export default EventViewer