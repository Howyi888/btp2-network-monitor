import { ArrowForwardIcon, ArrowUpDownIcon } from "@chakra-ui/icons";
import { Badge, Box, Divider, MenuItemOption, MenuOptionGroup, Table, Tbody, Td, Text, Th, Thead, Tr } from "@chakra-ui/react";
import { Menu, MenuButton, MenuList, Flex } from "@chakra-ui/react";
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
        <>{log.src_name}<ArrowForwardIcon />{log.dst_name}</>
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
            <MenuButton as={Flex}>{children}</MenuButton>
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
        <Thead position="sticky" top="0"><Tr ref={topLine} bg="gray.200">
            <Th>SN</Th>
            <Th>Time</Th>
            <Th><EventSelector>Event&bull;<ArrowUpDownIcon /></EventSelector></Th>
            <Th>Message</Th>
        </Tr></Thead>
        <Tbody className={bodyClass}>
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